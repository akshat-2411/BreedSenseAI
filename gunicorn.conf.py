"""
gunicorn.conf.py — Production server config for Render deployment
===================================================================
Tuned for Render's free tier (512MB RAM, shared CPU).
"""

import multiprocessing

# --- Workers ---
# Free tier has very limited RAM (~512MB). PyTorch alone uses ~400MB.
# Use 1 worker to avoid OOM kills. preload_app shares model across requests.
workers = 1
worker_class = "sync"

# --- Timeouts ---
# PyTorch inference on a shared CPU can be slow (20–60s).
# Default gunicorn timeout is 30s which kills the worker mid-prediction.
timeout = 120          # seconds before killing a worker
graceful_timeout = 30  # seconds for graceful shutdown
keepalive = 5

# --- Preload ---
# Load the app (and the ML model) once before forking workers.
# This dramatically reduces per-request memory and startup time.
preload_app = True

# --- Threads ---
# Single thread per worker — avoids GIL contention with PyTorch
threads = 1

# --- Logging ---
loglevel = "info"
accesslog = "-"   # stdout
errorlog = "-"    # stdout
