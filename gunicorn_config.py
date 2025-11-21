import os
import multiprocessing

# Gunicorn Configuration for Production

# Bind to the port defined in environment or default to 5000
port = os.getenv("PORT", "5000")
bind = f"0.0.0.0:{port}"

# Worker Configuration
# Limited to 2 workers and 2 threads for consistent resource usage
workers = 2
threads = 2
worker_class = "gthread"  # Use threads for concurrency within workers

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
