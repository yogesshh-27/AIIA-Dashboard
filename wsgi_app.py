"""
WSGI / ASGI compatibility entry point for Render deployment.
Supports:
  - gunicorn wsgi_app:app --bind 0.0.0.0:$PORT
  - uvicorn wsgi_app:app --host 0.0.0.0 --port $PORT
"""
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app_fastapi import app as fastapi_app

try:
    from a2wsgi import ASGIMiddleware
    # Expose WSGI callable for standard gunicorn workers
    app = ASGIMiddleware(fastapi_app)
except ImportError:
    app = fastapi_app
