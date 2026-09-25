"""
WSGI entry point for gunicorn on Render.
Usage: gunicorn wsgi_app:app --bind 0.0.0.0:$PORT
"""
from flask_app import create_app

app = create_app()
