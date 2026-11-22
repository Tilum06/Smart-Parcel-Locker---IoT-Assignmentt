"""Manual hardware adapter operating exclusively on a marked demo database."""
from dataclasses import asdict
from contextlib import closing
import json
import os
from pathlib import Path
import secrets
import sqlite3
import time
from typing import Literal
from uuid import uuid4

from backend.auth import hash_password
from backend.db import Database
from backend.devices import DeviceEvent, ingest
from backend.schemas import Input
from backend.services import payload_hash
from backend.state import BusinessError, transition

DEFAULT_DIRECTORY = Path(__file__).resolve().parent / 'data'
MARKER = 'smart-parcel-locker-development-only-v1'


class EventInput(Input):
    event_id: str
    transaction_id: str
    kind: Literal['UNLOCK_APPLIED', 'LOCK_APPLIED', 'DOOR_OPEN', 'DOOR_CLOSED', 'SENSOR', 'ERROR']
    door: Literal['OPEN', 'CLOSED', 'UNKNOWN'] = 'UNKNOWN'


class ConnectionInput(Input):
    online: bool


class Simulator:
    def __init__(self, directory: Path = DEFAULT_DIRECTORY) -> None:
        self.path = directory.resolve() / 'simulator.sqlite3'
        self.db = Database(str(self.path))
        self.accounts: list[dict] = []

    def initialize(self) -> None:
        production = [Path('backend/data/locker.sqlite3').resolve()]
        if os.getenv('LOCKER_DB_PATH'):
            production.append(Path(os.environ['LOCKER_DB_PATH']).resolve())
        if self.path.is_symlink() or any(
            self.path == path or (self.path.exists() and path.exists() and self.path.samefile(path))
            for path in production
        ):
            raise RuntimeError('Simulator refuses the production database')
        if self.path.exists():
            # Inspect read-only BEFORE initialization or any schema/data modification.
            with closing(sqlite3.connect(self.path.as_uri() + '?mode=ro', uri=True)) as conn:
                try:
                    marker = conn.execute('SELECT marker FROM demo_meta').fetchone()
                except sqlite3.OperationalError as exc:
                    raise RuntimeError('Refusing an existing database without the demo marker') from exc
                if not marker or marker[0] != MARKER:
                    raise RuntimeError('Invalid demo database marker')
        self.db.initialize()
        with self.db.write() as conn:
            conn.execute('CREATE TABLE IF NOT EXISTS demo_meta(marker TEXT PRIMARY KEY)')
            conn.execute('INSERT OR IGNORE INTO demo_meta VALUES (?)', (MARKER,))
            conn.execute('CREATE TABLE IF NOT EXISTS demo_hardware('
                         'locker_id TEXT PRIMARY KEY REFERENCES lockers(id), door TEXT NOT NULL)')
            conn.execute('CREATE TABLE IF NOT EXISTS demo_events('
                         'event_id TEXT PRIMARY KEY, payload_hash TEXT NOT NULL, event_json TEXT NOT NULL)')
            for locker_id in ('L01', 'L02'):
                conn.execute("INSERT OR IGNORE INTO demo_hardware VALUES (?,'UNKNOWN')", (locker_id,))
            conn.execute("UPDATE demo_hardware SET door='UNKNOWN'")
            conn.execute('UPDATE lockers SET online=0')
            # Credentials are random, demo-only, and rotate on restart.
            conn.execute('DELETE FROM auth_sessions')
            self.accounts = []
            for username, role, code, phone in [
                ('demo-admin', 'ADMIN', None, None), ('demo-kiosk', 'KIOSK', None, None),
                ('resident-001', 'RESIDENT', '001', '0000000001'),
                ('resident-002', 'RESIDENT', '002', '0000000002'),
            ]:
                resident_id = None
                if code:
                    conn.execute('INSERT OR IGNORE INTO rooms(room_code) VALUES (?)', (code,))
                    room_id = conn.execute('SELECT id FROM rooms WHERE room_code=?', (code,)).fetchone()[0]
                    conn.execute('INSERT OR IGNORE INTO residents(room_id,phone) VALUES (?,?)', (room_id, phone))
                    resident_id = conn.execute('SELECT id FROM residents WHERE room_id=? AND phone=?', (room_id, phone)).fetchone()[0]
                password = secrets.token_urlsafe(12)
                conn.execute('INSERT INTO accounts(username,password_hash,role,resident_id) VALUES (?,?,?,?) '
                             'ON CONFLICT(username) DO UPDATE SET password_hash=excluded.password_hash',
                             (username, hash_password(password), role, resident_id))
                self.accounts.append(dict(username=username, password=password, role=role, room_code=code, phone=phone))

    def reset(self) -> None:
        """Explicit demo reset only. Delete rows atomically, never remove database files."""
        with self.db.write() as conn:
            marker = conn.execute('SELECT marker FROM demo_meta').fetchone()
            if not marker or marker[0] != MARKER:
                raise RuntimeError('Refusing to reset an unmarked database')
            for table in ('demo_events', 'device_events', 'event_logs', 'request_records',
                          'kiosk_sessions', 'commands', 'transactions', 'parcels', 'auth_sessions'):
                conn.execute(f'DELETE FROM {table}')
            conn.execute("UPDATE lockers SET state='AVAILABLE',online=0,boot_id=NULL,last_sequence=-1,last_observed_at=0")
            conn.execute("UPDATE demo_hardware SET door='UNKNOWN'")

    def snapshot(self) -> dict:
        with self.db.read() as conn:
            conn.execute('BEGIN')
            result = {table: [dict(row) for row in conn.execute(f'SELECT * FROM {table}')]
                      for table in ('lockers', 'parcels', 'transactions', 'commands', 'event_logs', 'demo_hardware')}
            result['event_logs'].sort(key=lambda row: row['id'], reverse=True)
            result['kiosk_sessions'] = [dict(row) for row in conn.execute(
                'SELECT id,kiosk_id,parcel_id,resident_id,expires_at,used,attempts FROM kiosk_sessions')]
            result['residents'] = [dict(row) for row in conn.execute(
                'SELECT r.id,rm.room_code,r.phone,a.username FROM residents r JOIN rooms rm ON rm.id=r.room_id '
                'JOIN accounts a ON a.resident_id=r.id')]
            result['database'] = self.path.name
            result['server_time'] = time.time()
            return result

    def event(self, locker_id: str, data: EventInput) -> None:
        with self.db.read() as conn:
            previous = conn.execute('SELECT * FROM demo_events WHERE event_id=?', (data.event_id,)).fetchone()
            fingerprint = payload_hash({'locker_id': locker_id, **data.model_dump()})
            if previous:
                if previous['payload_hash'] != fingerprint:
                    raise BusinessError(409, 'request_id_payload_conflict')
                # A duplicate button request must not create a fresh sensor sample.
                return
            locker = conn.execute('SELECT * FROM lockers WHERE id=?', (locker_id,)).fetchone()
            if not locker:
                raise BusinessError(404, 'locker_not_found')
            if not locker['online']:
                raise BusinessError(409, 'node_offline')
            tx = conn.execute('SELECT * FROM transactions WHERE id=? AND locker_id=?',
                              (data.transaction_id, locker_id)).fetchone()
            if not tx or tx['status'] != 'PENDING':
                raise BusinessError(409, 'transaction_not_pending')
            hardware = conn.execute('SELECT door FROM demo_hardware WHERE locker_id=?', (locker_id,)).fetchone()
            command_id = None
            if data.kind in ('UNLOCK_APPLIED', 'LOCK_APPLIED'):
                action = 'UNLOCK' if data.kind == 'UNLOCK_APPLIED' else 'LOCK'
                cmd = conn.execute('SELECT id FROM commands WHERE transaction_id=? AND action=?', (tx['id'], action)).fetchone()
                if not cmd:
                    raise BusinessError(409, 'command_not_requested')
                command_id = cmd['id']
            door = {'DOOR_OPEN': 'OPEN', 'DOOR_CLOSED': 'CLOSED'}.get(data.kind, data.door)
            if data.kind in ('UNLOCK_APPLIED', 'LOCK_APPLIED'):
                door = hardware['door']  # Servo click never invents a CLOSED snapshot.
            event = DeviceEvent(event_id=data.event_id, transaction_id=tx['id'], locker_id=locker_id,
                                boot_id=locker['boot_id'] or f'demo-{uuid4()}',
                                sequence=locker['last_sequence'] + 1, observed_at=time.time(),
                                kind=data.kind, command_id=command_id, door=door)
        ingest(self.db, event)  # Actual Phase 1 state machine and completion checks.
        with self.db.write() as conn:
            conn.execute('INSERT INTO demo_events VALUES (?,?,?)',
                         (data.event_id, fingerprint, json.dumps(asdict(event))))
            if data.kind in ('DOOR_OPEN', 'DOOR_CLOSED', 'SENSOR'):
                conn.execute('UPDATE demo_hardware SET door=? WHERE locker_id=?', (door, locker_id))

    def connection(self, online: bool) -> None:
        if not online:
            with self.db.read() as conn:
                pending = conn.execute("SELECT t.*,l.boot_id,l.last_sequence FROM transactions t JOIN lockers l "
                                       "ON l.id=t.locker_id WHERE t.status='PENDING'").fetchall()
            for tx in pending:
                ingest(self.db, DeviceEvent(event_id=str(uuid4()), transaction_id=tx['id'], locker_id=tx['locker_id'],
                                            boot_id=tx['boot_id'] or f'demo-{uuid4()}', sequence=tx['last_sequence']+1,
                                            observed_at=time.time(), kind='OFFLINE'))
        with self.db.write() as conn:
            conn.execute('UPDATE lockers SET online=?', (int(online),))
            # Reconnect changes transport only: UNKNOWN/reservations remain untouched.
            conn.execute('INSERT INTO event_logs(event,created_at) VALUES (?,?)',
                         ('DEMO_NODE_CONNECTED' if online else 'DEMO_NODE_DISCONNECTED', time.time()))
