"""Development-only entry point; production backend.main stays unchanged."""
import asyncio
from contextlib import asynccontextmanager
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from backend.main import create_app
from .simulator import ConnectionInput, EventInput, Simulator


def create_demo_app(directory: Path | None = None):
    simulator = Simulator(directory) if directory is not None else Simulator()
    app = create_app(simulator.db)
    original_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(app):
        simulator.initialize()  # Refuse unmarked files BEFORE production initialization.
        async with original_lifespan(app):
            yield

    app.router.lifespan_context = lifespan
    app.title = 'Smart Parcel Locker — Development Simulator'
    app.state.simulator = simulator
    gate = asyncio.Lock()  # Serialize reset, manual hardware steps and normal API requests.

    @app.middleware('http')
    async def local_development_only(request: Request, call_next):
        try:
            local = request.client is not None and ip_address(request.client.host).is_loopback
        except ValueError:
            local = False
        host = urlsplit(str(request.url)).hostname
        origin = request.headers.get('origin')
        expected_origin = str(request.base_url).rstrip('/')
        if (not local or host not in ('127.0.0.1', 'localhost', '::1')
                or (origin and origin != expected_origin)
                or request.headers.get('sec-fetch-site') == 'cross-site'):
            return JSONResponse(status_code=403, content={'detail': 'localhost_only'})
        if request.method not in ('GET', 'HEAD', 'OPTIONS') and request.headers.get('x-demo-control') != '1':
            return JSONResponse(status_code=403, content={'detail': 'demo_control_header_required'})
        async with gate:
            response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'"
        return response

    @app.get('/demo/bootstrap')
    def bootstrap() -> dict:
        return {'mode': 'DEVELOPMENT ONLY', 'accounts': simulator.accounts, 'database': simulator.path.name}

    @app.get('/demo/state')
    def state() -> dict:
        return simulator.snapshot()

    @app.post('/demo/node')
    def node(data: ConnectionInput) -> dict:
        simulator.connection(data.online)
        return simulator.snapshot()

    @app.post('/demo/lockers/{locker_id}/events')
    def event(locker_id: str, data: EventInput) -> dict:
        simulator.event(locker_id, data)
        return simulator.snapshot()

    @app.post('/demo/reset')
    def reset() -> dict:
        simulator.reset()
        return simulator.snapshot()

    static = Path(__file__).resolve().parent / 'static'
    app.mount('/assets', StaticFiles(directory=static), name='demo-assets')

    @app.get('/', include_in_schema=False)
    def index():
        return FileResponse(static / 'index.html')

    return app
