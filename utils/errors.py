from datetime import datetime, timezone

class APIError(Exception):
    """Base class for API errors"""
    def __init__(self, message, status_code=500, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['code'] = self.status_code
        rv['timestamp'] = datetime.now(timezone.utc).isoformat()
        return rv
