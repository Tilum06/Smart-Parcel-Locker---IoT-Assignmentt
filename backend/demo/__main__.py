"""Only the fixed loopback address is supported. One worker, no proxy trust."""
import argparse
import uvicorn
from .app import create_demo_app


def main() -> None:
    parser = argparse.ArgumentParser(description='Local-only Smart Parcel Locker simulator')
    parser.add_argument('--port', type=int, default=8001)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('port must be 1–65535')
    uvicorn.run(create_demo_app(), host='127.0.0.1', port=args.port, proxy_headers=False)


if __name__ == '__main__':
    main()
