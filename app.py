from flask import Flask, request, jsonify
from classify import classify_ticket
import logging
import os

app = Flask(__name__)

# 🔧 Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200


@app.route('/classify', methods=['POST'])
def classify():
    """Classifies incoming support ticket text"""
    data = request.get_json()

    if not data or "ticket" not in data:
        logger.warning("Bad request: Missing 'ticket' field")
        return jsonify({"error": "Missing 'ticket' field"}), 400

    ticket_text = data["ticket"]

    try:
        category = classify_ticket(ticket_text)
        return jsonify({"category": category}), 200

    except Exception as e:
        logger.error(f"Classification failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
