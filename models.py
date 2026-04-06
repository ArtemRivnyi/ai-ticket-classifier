from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(100), nullable=False, index=True)
    correct = db.Column(db.Boolean, nullable=False)
    ticket = db.Column(db.Text, nullable=True)
    predicted = db.Column(db.String(100), nullable=True)
    comments = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "request_id": self.request_id,
            "correct": self.correct,
            "ticket": self.ticket,
            "predicted": self.predicted,
            "comments": self.comments,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
