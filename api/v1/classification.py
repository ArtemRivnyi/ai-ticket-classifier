from flask import Blueprint, request, jsonify, current_app
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Dict
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from extensions import limiter
from middleware.auth import require_api_key

logger = logging.getLogger(__name__)

classification_bp = Blueprint("classification", __name__)

class TicketRequest(BaseModel):
    ticket: str = Field(..., min_length=10, max_length=10000)

class BatchTicketRequest(BaseModel):
    tickets: List[str] = Field(..., min_length=1, max_length=100)

def sanitize_text(text: str) -> str:
    if not text: return ""
    import bleach
    import re
    text = text.replace("\x00", "")
    text = bleach.clean(text, strip=True)
    text = re.sub(r"\s+", " ", text)
    return text[:5000].strip()

@classification_bp.route("/classify", methods=["POST"])
@require_api_key
@limiter.limit("60 per minute")
def classify():
    classifier = current_app.config.get("CLASSIFIER")
    if not classifier:
        return jsonify({"error": "Service unavailable"}), 503
    
    try:
        data = TicketRequest(**request.json)
        ticket = sanitize_text(data.ticket)
        result = classifier.classify(ticket)
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 400
    except Exception as e:
        logger.error(f"Classification error: {e}")
        return jsonify({"error": "Internal error", "message": str(e)}), 500

@classification_bp.route("/batch", methods=["POST"])
@require_api_key
@limiter.limit("10 per minute")
def batch_classify():
    classifier = current_app.config.get("CLASSIFIER")
    if not classifier:
        return jsonify({"error": "Service unavailable"}), 503
    
    try:
        data = BatchTicketRequest(**request.json)
        tickets = [sanitize_text(t) for t in data.tickets if t]
        
        results = [None] * len(tickets)
        errors = []
        # Parallel processing
        with ThreadPoolExecutor(max_workers=min(len(tickets), 10)) as executor:
            def task(i, t):
                try:
                    results[i] = classifier.classify(t)
                except Exception as e:
                    errors.append({"index": i, "error": str(e)})
            
            futures = [executor.submit(task, i, t) for i, t in enumerate(tickets)]
            for f in futures: f.result()
        
        return jsonify({
            "total": len(tickets),
            "successful": len([r for r in results if r]),
            "results": [r for r in results if r],
            "errors": errors
        }), 200
    except Exception as e:
        return jsonify({"error": "Batch error", "message": str(e)}), 500
