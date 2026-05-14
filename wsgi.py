"""
wsgi.py — WSGI entry point for gunicorn
========================================
Creates the Flask app once at module level so that gunicorn's
`preload_app = True` can share it across workers without reloading
the PyTorch model on every request.
"""

# MUST be set before ANY other import — PyTorch's autograd graph traversal
# through ResNet residual connections causes deep Python recursion.
# Setting this here ensures gunicorn workers inherit the limit via fork.
import sys
sys.setrecursionlimit(50000)

from app import create_app

application = create_app()

# Also expose as 'app' for compatibility
app = application
