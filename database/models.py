from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone
import os

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(20), default="user")  # user, admin
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user")

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    key_hash = Column(String(64), unique=True, nullable=False)
    name = Column(String(50)) # e.g. "Production Key"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tier = Column(String(20), default="free")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_used = Column(DateTime)
    total_requests = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="api_keys")

class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True)
    api_key_hash = Column(String(64), index=True)
    endpoint = Column(String(100))
    category = Column(String(50))
    duration = Column(Float)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status_code = Column(Integer)

# Database connection
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/ai_ticket_classifier"
)

# Handle SQLite fallback for local testing without docker
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database"""
    Base.metadata.create_all(engine)

def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
