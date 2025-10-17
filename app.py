from flask import Flask, request, jsonify
from classify import classify_ticket
import logging
import os

app = Flask(__name__)

# Настройка логов (чтобы видеть запросы в Docker-логах)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/classify', methods=['POST'])
def classify():
    data = request.get_json()
    ticket_text = data.get("ticket")

    if not ticket_text:
        app.logger.warning("Received empty ticket request")
        return jsonify({"error": "Missing 'ticket' field"}), 400

    app.logger.info(f"Classifying ticket: {ticket_text}")
    category = classify_ticket(ticket_text)
    return jsonify({"category": category})

# 🔹 Добавим health-check endpoint для Docker / CI
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    # Если переменная окружения FLASK_ENV установлена — это dev
    is_debug = os.getenv("FLASK_ENV") == "development"

    app.run(
        host='0.0.0.0',  # слушает все интерфейсы (нужно для Docker)
        port=5000,
        debug=is_debug
    )
