import multiprocessing
import os

# Gunicorn configuration

# Bind to 0.0.0.0:$PORT or default to 5000
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"

# Worker configuration
# Limit workers to prevent memory exhaustion on free tier
workers = 2  # Fixed number of workers for stability
threads = 4  # Threads per worker for concurrency
worker_class = 'gthread'  # Threaded worker for I/O bound tasks

# Timeouts
timeout = 120  # 2 minutes timeout for long AI requests
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'ai-ticket-classifier'

# Preload application for memory efficiency
preload_app = True
