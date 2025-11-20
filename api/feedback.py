"""
Feedback API for collecting user feedback on classifications
"""

from flask import Blueprint, request, jsonify
from pydantic import BaseModel, Field
from typing import Optional
import time
from datetime import datetime, timezone
import os

feedback_bp = Blueprint('feedback', __name__)

# Simple in-memory storage for feedback (in production, use Redis or database)
feedback_storage = {}
feedback_stats = {
    'total': 0,
    'correct': 0,
    'incorrect': 0
}

class FeedbackRequest(BaseModel):
    """Feedback request model"""
    request_id: str = Field(..., description="Request ID from classification")
    correct: bool = Field(..., description="Was the classification correct?")
    comment: Optional[str] = Field(None, max_length=500, description="Optional comment")

@feedback_bp.route('/api/v1/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback for a classification"""
    try:
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        try:
            data = FeedbackRequest(**request.json)
        except Exception as e:
            return jsonify({
                'error': 'Validation error',
                'message': str(e)
            }), 400
        
        # Store feedback
        feedback_entry = {
            'request_id': data.request_id,
            'correct': data.correct,
            'comment': data.comment,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'ip': request.remote_addr
        }
        
        feedback_storage[data.request_id] = feedback_entry
        
        # Update stats
        feedback_stats['total'] += 1
        if data.correct:
            feedback_stats['correct'] += 1
        else:
            feedback_stats['incorrect'] += 1
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your feedback!',
            'request_id': data.request_id
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e) if os.getenv('FLASK_ENV') == 'development' else 'An error occurred'
        }), 500

@feedback_bp.route('/api/v1/feedback/stats', methods=['GET'])
def get_feedback_stats():
    """Get feedback statistics"""
    try:
        accuracy = 0
        if feedback_stats['total'] > 0:
            accuracy = round((feedback_stats['correct'] / feedback_stats['total']) * 100, 2)
        
        return jsonify({
            'total_feedback': feedback_stats['total'],
            'correct': feedback_stats['correct'],
            'incorrect': feedback_stats['incorrect'],
            'accuracy': accuracy,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@feedback_bp.route('/api/v1/feedback/<request_id>', methods=['GET'])
def get_feedback(request_id):
    """Get feedback for a specific request"""
    try:
        if request_id in feedback_storage:
            return jsonify(feedback_storage[request_id]), 200
        else:
            return jsonify({'error': 'Feedback not found'}), 404
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500
