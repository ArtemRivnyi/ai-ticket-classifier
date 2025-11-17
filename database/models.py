from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class APIKey(Base):
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True)
    key_hash = Column(String(64), unique=True, nullable=False)
    tier = Column(String(20), default='free')
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    total_requests = Column(Integer, default=0)

class UsageLog(Base):
    __tablename__ = 'usage_logs'
    
    id = Column(Integer, primary_key=True)
    api_key_hash = Column(String(64))
    endpoint = Column(String(100))
    category = Column(String(50))
    duration = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status_code = Column(Integer)

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://classifier:secure_pass@postgres:5432/classifier_db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Initialize database"""
    Base.metadata.create_all(engine)
