from flask import Flask, request, jsonify
from classify import classify_ticket
import logging
from logging.handlers import RotatingFileHandler
import os
import traceback
from pydantic import BaseModel, ValidationError  # Добавляем импорт pydantic

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
if not any(isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", None) == os.path.abspath(LOG_PATH) for h in root_logger.handlers):
    root_logger.addHandler(handler)
if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
    root_logger.addHandler(logging.StreamHandler())

app.logger = root_logger.getChild("ai-ticket-classifier")

# ===== Helpers =====
def make_error(message: str, code: int = 500, details: str | None = None):
    body = {"error": message}
    if details:
        body["details"] = details
    return jsonify(body), code

# ===== Pydantic model for validation =====
class TicketInput(BaseModel):
    ticket: str
    priority: str | None = None

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
        if not data:
            app.logger.warning("Bad request - no JSON data")
            return make_error("Invalid JSON", 400)

        # Validate input using pydantic
        try:
            ticket_input = TicketInput(**data)
        except ValidationError as e:
            app.logger.warning(f"Validation error: {e}")
            return make_error("Invalid input", 400, details=str(e))

        ticket_text = ticket_input.ticket
        app.logger.info("Received ticket for classification", extra={"ticket": ticket_text, "priority": ticket_input.priority})

        category = classify_ticket(ticket_text)
        if not category or category.lower() in ("error", "unknown"):
            app.logger.error(f"Classification returned invalid result: {category}")
            return make_error("Classification failed", 502)

        app.logger.info(f"Ticket classified -> {category}")
        return jsonify({"category": category, "priority": ticket_input.priority or "medium"}), 200

    except Exception as exc:
        tb = traceback.format_exc()
        app.logger.error(f"Unhandled exception in /api/v1/classify: {exc}\n{tb}")
        return make_error("Internal server error", 500, details=str(exc))

# ===== Run server =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.logger.info(f"Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)