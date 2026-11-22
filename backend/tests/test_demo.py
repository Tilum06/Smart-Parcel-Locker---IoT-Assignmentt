"""Integration tests for the separate development app; baseline tests stay untouched."""
import hashlib
from pathlib import Path
import time
from uuid import uuid4

from fastapi.testclient import TestClient
import pytest
from backend.db import Database
from backend.demo.app import create_demo_app
from backend.main import create_app

CONTROL = {'X-Demo-Control': '1'}


@pytest.fixture
def demo(tmp_path):
    app = create_demo_app(tmp_path / 'demo')
    with TestClient(app, base_url='http://127.0.0.1', client=('127.0.0.1', 50000)) as client:
        yield client, app.state.simulator


def login(client, role='KIOSK', username=None):
    accounts = client.get('/demo/bootstrap').json()['accounts']
    account = next(a for a in accounts if a['username'] == username) if username else next(a for a in accounts if a['role'] == role)
    response = client.post('/api/v1/auth/login', json={key: account[key] for key in ('username', 'password')}, headers=CONTROL)
    assert response.status_code == 200, response.text
    return {**CONTROL, 'Authorization': 'Bearer ' + response.json()['access_token'], 'X-Request-ID': str(uuid4())}


def allocate_demo(client):
    client.post('/demo/node', json={'online': True}, headers=CONTROL).raise_for_status()
    token = login(client)
    response = client.post('/api/v1/deposits', json=dict(room_code='001', recipient_phone='0000000001', parcel_size='S'), headers=token)
    assert response.status_code == 201, response.text
    return response.json(), token


def event(client, item, kind, **kwargs):
    return client.post(f"/demo/lockers/{item['locker_id']}/events", headers=CONTROL,
                       json=dict(event_id=str(uuid4()), transaction_id=item['transaction_id'], kind=kind, **kwargs))


def cycle(client, item):
    for kind in ('UNLOCK_APPLIED', 'DOOR_OPEN', 'DOOR_CLOSED'):
        response = event(client, item, kind)
        assert response.status_code == 200, response.text


def store(client):
    item, token = allocate_demo(client)
    cycle(client, item)
    client.post(f"/api/v1/deposits/{item['parcel_id']}/confirm", headers={**token, 'X-Request-ID': str(uuid4())}).raise_for_status()
    response = event(client, item, 'LOCK_APPLIED')
    assert response.status_code == 200, response.text
    return item, token


def test_separate_database_starts_offline_no_secret_in_snapshot(demo):
    client, sim = demo
    state = client.get('/demo/state').json()
    assert [(l['id'], l['size'], l['online']) for l in state['lockers']] == [('L01', 'S', 0), ('L02', 'M', 0)]
    assert sim.path.name == 'simulator.sqlite3'
    assert 'password' not in str(state) and 'code_hash' not in str(state)
    assert state['transactions'] == [] and state['commands'] == []


def test_manual_full_deposit_and_pickup_real_auth(demo):
    client, _ = demo
    item, kiosk = store(client)
    state = client.get('/demo/state').json()
    assert state['parcels'][0]['status'] == 'STORED'
    resident = login(client, username='resident-001')
    session = client.post('/api/v1/kiosk-sessions', headers={**kiosk, 'X-Request-ID': str(uuid4())}, json={'parcel_id': item['parcel_id']})
    assert session.status_code == 201
    payload = {key: session.json()[key] for key in ('session_id', 'code')}
    response = client.post(f"/api/v1/pickups/{item['parcel_id']}", headers=resident, json=payload)
    assert response.status_code == 200, response.text
    pickup = response.json()
    cycle(client, pickup)
    client.post(f"/api/v1/pickups/{item['parcel_id']}/confirm", headers={**resident, 'X-Request-ID': str(uuid4())}).raise_for_status()
    state = event(client, pickup, 'LOCK_APPLIED').json()
    assert state['parcels'][0]['status'] == 'COMPLETED'
    assert state['lockers'][0]['state'] == 'AVAILABLE'
    assert all(not tx['active'] for tx in state['transactions'])
    assert any(e['event'] == 'USER_CONFIRMED' for e in state['event_logs'])


def test_no_automatic_evidence_or_completion(demo):
    client, _ = demo
    item, token = allocate_demo(client)
    state = client.get('/demo/state').json()
    assert state['parcels'][0]['status'] == 'CREATED'
    assert state['commands'][0]['status'] == 'PENDING'
    assert event(client, item, 'LOCK_APPLIED').status_code == 409
    cycle(client, item)
    assert event(client, item, 'LOCK_APPLIED').status_code == 409  # No confirmation, no LOCK intent.
    client.post(f"/api/v1/deposits/{item['parcel_id']}/confirm", headers={**token, 'X-Request-ID': str(uuid4())})
    state = client.get('/demo/state').json()
    assert state['lockers'][0]['state'] == 'DEPOSITING'
    assert state['transactions'][0]['active'] == 1


@pytest.mark.parametrize('action', ['disconnect', 'error'])
def test_fault_or_disconnect_never_frees_reserved_locker(demo, action):
    client, _ = demo
    item, _ = allocate_demo(client)
    if action == 'disconnect':
        response = client.post('/demo/node', json={'online': False}, headers=CONTROL)
    else:
        response = event(client, item, 'ERROR')
    assert response.status_code == 200, response.text
    client.post('/demo/node', json={'online': True}, headers=CONTROL)
    state = client.get('/demo/state').json()
    assert state['lockers'][0]['state'] == 'UNKNOWN'
    assert state['transactions'][0]['status'] == 'EXCEPTION'
    assert state['transactions'][0]['active'] == 1


def test_event_duplicate_does_not_create_new_sensor_evidence(demo):
    client, _ = demo
    item, _ = allocate_demo(client)
    data = dict(event_id=str(uuid4()), transaction_id=item['transaction_id'], kind='UNLOCK_APPLIED')
    url = f"/demo/lockers/{item['locker_id']}/events"
    first = client.post(url, headers=CONTROL, json=data)
    second = client.post(url, headers=CONTROL, json=data)
    assert first.status_code == second.status_code == 200
    assert first.json()['lockers'][0]['last_sequence'] == second.json()['lockers'][0]['last_sequence']
    assert client.post(url, headers=CONTROL, json={**data, 'kind': 'DOOR_OPEN'}).status_code == 409


def test_reset_is_explicit_revokes_tokens_and_only_clears_demo(demo):
    client, sim = demo
    item, token = allocate_demo(client)
    assert client.post('/demo/reset').status_code == 403
    assert client.get('/demo/state').json()['transactions'][0]['active'] == 1
    state = client.post('/demo/reset', headers=CONTROL).json()
    assert state['parcels'] == state['transactions'] == state['commands'] == []
    assert all(l['state'] == 'AVAILABLE' and l['online'] == 0 for l in state['lockers'])
    assert client.get('/api/v1/lockers', headers=token).status_code == 401
    assert sim.path.exists()


def test_localhost_origin_and_mutation_guards(demo):
    client, _ = demo
    assert client.get('/demo/state', headers={'Host': 'evil.example'}).status_code == 403
    assert client.get('/demo/bootstrap', headers={'Origin': 'https://evil.example'}).status_code == 403
    assert client.post('/demo/node', json={'online': True}).status_code == 403
    assert client.post('/demo/node', headers={**CONTROL, 'Origin': 'https://evil.example'}, json={'online': True}).status_code == 403
    with TestClient(client.app, base_url='http://127.0.0.1', client=('192.0.2.1', 50000)) as remote:
        assert remote.get('/demo/state').status_code == 403


def test_refuses_unmarked_database_without_modification(tmp_path):
    directory = tmp_path / 'foreign'
    db = Database(str(directory / 'simulator.sqlite3'))
    db.initialize()
    before = hashlib.sha256(Path(db.path).read_bytes()).digest()
    with pytest.raises(RuntimeError, match='without the demo marker'):
        with TestClient(create_demo_app(directory)):
            pass
    assert hashlib.sha256(Path(db.path).read_bytes()).digest() == before


def test_production_database_and_routes_untouched(tmp_path, monkeypatch):
    production = tmp_path / 'production.sqlite3'
    db = Database(str(production))
    db.initialize()
    before = production.read_bytes()
    monkeypatch.setenv('LOCKER_DB_PATH', str(production))
    with TestClient(create_demo_app(tmp_path / 'demo'), base_url='http://localhost', client=('127.0.0.1', 50000)) as client:
        client.post('/demo/reset', headers=CONTROL).raise_for_status()
    assert production.read_bytes() == before
    paths = create_app(db).openapi()['paths']
    assert not any(path.startswith('/demo') for path in paths)


def test_kiosk_ttl_and_other_resident_authorization_are_reused(demo):
    client, sim = demo
    item, kiosk = store(client)
    alice = login(client, username='resident-001')
    bob = login(client, username='resident-002')
    response = client.post('/api/v1/kiosk-sessions', headers={**kiosk, 'X-Request-ID': str(uuid4())}, json={'parcel_id': item['parcel_id']})
    session = response.json()
    assert 29 <= session['expires_at'] - time.time() <= 30
    payload = {key: session[key] for key in ('session_id', 'code')}
    url = f"/api/v1/pickups/{item['parcel_id']}"
    assert client.post(url, headers=bob, json=payload).status_code == 403
    with sim.db.write() as conn:
        conn.execute('UPDATE kiosk_sessions SET expires_at=?', (time.time()-1,))
    assert client.post(url, headers=alice, json=payload).status_code == 403


def test_frontend_assets_are_local_and_absent_from_production(demo, tmp_path):
    client, _ = demo
    page = client.get('/')
    assert page.status_code == 200
    assert '<html lang="vi">' in page.text
    assert '/assets/app.js' in page.text and '/assets/app.css' in page.text
    assert "frame-ancestors 'none'" in page.headers['content-security-policy']
    assert page.headers['cache-control'] == 'no-store'
    for asset in ('app.js', 'app.css'):
        assert client.get('/assets/' + asset).status_code == 200
    with TestClient(create_app(Database(str(tmp_path / 'prod.sqlite3')))) as production:
        assert production.get('/').status_code == 404
        assert production.get('/assets/app.js').status_code == 404
        assert production.post('/demo/reset').status_code == 404


def test_restart_retains_reservation_and_requires_manual_reconnect(demo):
    client, sim = demo
    item, _ = allocate_demo(client)
    with TestClient(create_demo_app(sim.path.parent), base_url='http://127.0.0.1', client=('127.0.0.1', 50001)) as restarted:
        state = restarted.get('/demo/state').json()
        locker = next(l for l in state['lockers'] if l['id'] == item['locker_id'])
        assert locker['online'] == 0 and locker['state'] == 'RESERVED'
        assert state['transactions'][0]['active'] == 1
        assert state['commands'][0]['status'] == 'PENDING'
        assert event(restarted, item, 'UNLOCK_APPLIED').status_code == 409


def test_stale_closed_requires_another_manual_snapshot(demo):
    client, sim = demo
    item, token = allocate_demo(client)
    cycle(client, item)
    client.post(f"/api/v1/deposits/{item['parcel_id']}/confirm", headers={**token, 'X-Request-ID': str(uuid4())}).raise_for_status()
    with sim.db.write() as conn:
        conn.execute('UPDATE transactions SET closed_at=?', (time.time() - 11,))
    state = event(client, item, 'LOCK_APPLIED').json()
    assert state['parcels'][0]['status'] == 'DEPOSITING'
    assert state['lockers'][0]['state'] == 'DEPOSITING'
    assert client.get('/demo/state').json()['transactions'][0]['active'] == 1
    state = event(client, item, 'SENSOR', door='CLOSED').json()
    assert state['parcels'][0]['status'] == 'STORED'
