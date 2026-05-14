"""
wsgi.py — WSGI entry point for gunicorn
========================================
Creates the Flask app once at module level so that gunicorn's
`preload_app = True` can share it across workers without reloading
the PyTorch model on every request.
"""

from app import create_app

application = create_app()

# Also expose as 'app' for compatibility
app = application
