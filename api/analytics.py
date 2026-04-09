from flask import Blueprint, jsonify, request
from models import db, Feedback
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
import logging
import os

logger = logging.getLogger(__name__)

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/api/analytics/stats", methods=["GET"])
def get_analytics_stats():
    """Get analytics stats for the dashboard charts"""
    try:
        # Timezone-aware date calculations
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)
        
        # 1. Accuracy over time
        # Note: func.date is dialect-dependent but usually works for basic grouping
        try:
            daily_accuracy = db.session.query(
                func.date(Feedback.timestamp).label("date"),
                func.avg(Feedback.correct.cast(db.Integer)).label("avg_accuracy")
            ).filter(Feedback.timestamp >= seven_days_ago)\
             .group_by(func.date(Feedback.timestamp))\
             .order_by(func.date(Feedback.timestamp))\
             .all()
        except Exception as e:
            logger.warning(f"Accuracy query failed, likely dialect mismatch: {e}")
            daily_accuracy = []
        
        accuracy_data = [
            {"date": str(d.date), "accuracy": round(float(d.avg_accuracy or 0) * 100, 2)}
            for d in daily_accuracy
        ]

        # 2. Category distribution
        categories = db.session.query(
            Feedback.predicted,
            func.count(Feedback.id).label("count")
        ).group_by(Feedback.predicted)\
         .order_by(func.desc("count"))\
         .limit(5)\
         .all()
        
        category_data = [
            {"category": (c.predicted if c.predicted else "Other"), "count": c.count}
            for c in categories
        ]

        # 3. Recent volume
        volume = db.session.query(
            func.date(Feedback.timestamp).label("date"),
            func.count(Feedback.id).label("count")
        ).filter(Feedback.timestamp >= seven_days_ago)\
         .group_by(func.date(Feedback.timestamp))\
         .order_by(func.date(Feedback.timestamp))\
         .all()
        
        volume_data = [
            {"date": str(v.date), "count": v.count}
            for v in volume
        ]

        return jsonify({
            "accuracy_over_time": accuracy_data,
            "category_distribution": category_data,
            "request_volume": volume_data
        }), 200

    except Exception as e:
        logger.error(f"Analytics failure: {e}")
        # Return empty stats instead of 500 for a better UX
        return jsonify({
            "accuracy_over_time": [],
            "category_distribution": [],
            "request_volume": [],
            "error_info": str(e) if os.getenv("FLASK_ENV") == "development" else None
        }), 200
