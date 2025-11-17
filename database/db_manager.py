from database.models import SessionLocal, APIKey, UsageLog
from datetime import datetime
import hashlib

class DatabaseManager:
    def __init__(self):
        self.session = SessionLocal()
    
    def log_usage(self, api_key, endpoint, category, duration, status_code):
        """Log API usage"""
        try:
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            log = UsageLog(
                api_key_hash=key_hash,
                endpoint=endpoint,
                category=category,
                duration=duration,
                status_code=status_code
            )
            self.session.add(log)
            
            # Update API key stats
            api_key_obj = self.session.query(APIKey).filter_by(key_hash=key_hash).first()
            if api_key_obj:
                api_key_obj.total_requests += 1
                api_key_obj.last_used = datetime.utcnow()
            
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"DB Error: {e}")
    
    def get_usage_stats(self, api_key_hash):
        """Get usage statistics"""
        logs = self.session.query(UsageLog).filter_by(api_key_hash=api_key_hash).all()
        return {
            'total_requests': len(logs),
            'categories': {}
        }
