"""
WSGI / ASGI compatibility entry point for Render deployment.
Supports:
  - gunicorn wsgi_app:app --bind 0.0.0.0:$PORT (WSGI)
  - uvicorn wsgi_app:app --host 0.0.0.0 --port $PORT (ASGI)
  - gunicorn wsgi_app:app -k uvicorn.workers.UvicornWorker (ASGI with Gunicorn)
"""
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app_fastapi import app as fastapi_app

try:
    from a2wsgi import ASGIMiddleware
    wsgi_middleware = ASGIMiddleware(fastapi_app)
except Exception:
    wsgi_middleware = None

class UniversalApp:
    """Universal callable responding to both ASGI (3 args) and WSGI (2 args)."""
    def __call__(self, *args, **kwargs):
        if len(args) == 3 or "scope" in kwargs or "receive" in kwargs:
            # Called by ASGI server (uvicorn)
            return fastapi_app(*args, **kwargs)
        # Called by WSGI server (gunicorn sync)
        if wsgi_middleware is not None:
            return wsgi_middleware(*args, **kwargs)
        return fastapi_app(*args, **kwargs)

    def __getattr__(self, item):
        return getattr(fastapi_app, item)

app = UniversalApp()
