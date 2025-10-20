# 🤖 AI Ticket Classifier

**AI Ticket Classifier** is a lightweight, AI-powered backend built with **Flask**, **OpenAI GPT-4o-mini**, and **Docker Compose**.  
It automatically classifies incoming support tickets into categories such as *Network Issue*, *Account Problem*, or *Payment Issue*, and can generate suggested responses. Ideal for small tech teams, helpdesks, or e-commerce support.

---

## ✨ Features

- 🧠 **AI-Powered Classification** with GPT-4o-mini
- ⚙️ **RESTful API** with `/api/v1/classify` and `/api/v1/health` endpoints
- 🐳 **Docker & Docker Compose Ready** — deploy anywhere in seconds
- 🔁 Automatic restart and container health monitoring
- 💡 Easy to extend with new categories or multilingual support

---

## 🛠️ Technologies Used

- Python 3.10+
- Flask
- Gunicorn
- Docker + Docker Compose
- OpenAI API (GPT-4o-mini)

---

## 🚀 Quick Start

### 1️⃣ Clone the repository
```bash
git clone https://github.com/ArtemRivnyi/ai-ticket-classifier.git
cd ai-ticket-classifier
```

### 2️⃣ Configure API key
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=sk-your-key-here
```

### 3️⃣ Run with Docker Compose
Build and start the service:
```bash
docker compose up --build
```

Stop the service:
```bash
docker compose down
```

---

### 4️⃣ Test the API

**Health check:**
```bash
curl http://127.0.0.1:5000/api/v1/health
```

**Classify a ticket:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/classify \
-H "Content-Type: application/json" \
-d '{"ticket":"I cannot connect to the VPN"}'
```

**Expected response:**
```json
{
  "category": "Network Issue",
  "suggested_response": "Please check your VPN connection and try again..."
}
```

---

## 🧩 Example Categories

| Category        | Example Ticket                                 |
| --------------- | ---------------------------------------------- |
| Network Issue   | “VPN not connecting”, “Wi-Fi drops constantly” |
| Account Problem | “Can’t log in”, “Password reset fails”         |
| Payment Issue   | “Refund request”, “Invoice missing”            |
| Feature Request | “Add dark mode”                                |
| Other           | Anything else                                  |

---

## 🧠 Planned Improvements

- JSON Schema validation (Pydantic)
- Retry logic for OpenAI rate limits
- GitHub Actions CI/CD
- Cloud deployment (Render, Railway, or AWS)
- Structured logging and metrics
- Multilingual ticket support
- Web dashboard for ticket review and knowledge base management

---

## 🧰 Maintainer

**Artem Rivnyi** — Junior Technical Support / DevOps Enthusiast  
📧 [artemrivnyi@outlook.com](mailto:artemrivnyi@outlook.com)  
🔗 [LinkedIn](https://www.linkedin.com/in/artemrivnyi)
