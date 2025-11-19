import os
import multiprocessing

# Gunicorn Configuration for Production

# Bind to the port defined in environment or default to 5000
port = os.getenv("PORT", "5000")
bind = f"0.0.0.0:{port}"

# Worker Configuration
# Recommended: 2 * cpu_cores + 1
workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"  # Use 'gevent' for async if needed, but 'sync' is safer for CPU-bound tasks

# Timeouts
# 120s timeout to handle long-running AI requests (Gemini/OpenAI)
timeout = 120
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process Naming
proc_name = "ai-ticket-classifier"

# Preload application for memory efficiency
preload_app = True
