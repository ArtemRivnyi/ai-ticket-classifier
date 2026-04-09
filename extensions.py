from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

# Shared extensions
db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address, default_limits=["1000 per day", "100 per hour"])
cache = Cache()
