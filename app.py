from flask import Flask, request, jsonify
from classify import classify_ticket

app = Flask(__name__)

@app.route('/classify', methods=['POST'])
def classify():
    data = request.get_json()
    ticket_text = data.get("ticket")

    if not ticket_text:
        return jsonify({"error": "Missing 'ticket' field"}), 400

    category = classify_ticket(ticket_text)
    return jsonify({"category": category})

if __name__ == '__main__':
    app.run(debug=True)
