from flask import Flask, request, jsonify
from classify import classify_ticket
import logging
from logging.handlers import RotatingFileHandler
import os
import traceback

app = Flask(__name__)

# ===== Logging setup =====
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "app.log")

handler = RotatingFileHandler(LOG_PATH, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)

# Root logger settings
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
# avoid duplicate handlers if reloading
if not any(isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", None) == os.path.abspath(LOG_PATH) for h in root_logger.handlers):
    root_logger.addHandler(handler)
# always also log to console
if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
    root_logger.addHandler(logging.StreamHandler())

app.logger = root_logger.getChild("ai-ticket-classifier")

# ===== Helpers =====
def make_error(message: str, code: int = 500, details: str | None = None):
    body = {"error": message}
    if details:
        body["details"] = details
    return jsonify(body), code

# ===== Health endpoint =====
@app.route("/api/v1/health", methods=["GET"])
def health():
    app.logger.info("Health check called")
    return jsonify({"status": "ok"}), 200

# ===== Classification endpoint (versioned) =====
@app.route("/api/v1/classify", methods=["POST"])
def classify():
    try:
        data = request.get_json(silent=True)
        if not data or "ticket" not in data:
            app.logger.warning("Bad request - missing 'ticket' field")
            return make_error("Missing 'ticket' field", 400)

        ticket_text = data["ticket"]
        app.logger.info("Received ticket for classification", extra={"ticket": ticket_text})

        category = classify_ticket(ticket_text)
        # If classify_ticket returns "Error" or similar, treat as 502
        if not category or category.lower() in ("error", "unknown"):
            app.logger.error(f"Classification returned invalid result: {category}")
            return make_error("Classification failed", 502)

        app.logger.info(f"Ticket classified -> {category}")
        return jsonify({"category": category}), 200

    except Exception as exc:
        tb = traceback.format_exc()
        app.logger.error(f"Unhandled exception in /api/v1/classify: {exc}\n{tb}")
        return make_error("Internal server error", 500, details=str(exc))

# ===== Run server =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.logger.info(f"Starting Flask server on port {port}")
    # Временно включаем debug mode
    app.run(host="0.0.0.0", port=port, debug=True)
