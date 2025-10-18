# 🤖 AI Ticket Classifier API

A lightweight AI-powered backend service built with **Flask**, **OpenAI GPT-4o-mini**, and **Docker**.  
It classifies incoming support tickets into predefined categories such as *Network Issue*, *Login Problem*, or *Payment Issue*.  
Ideal for automating customer support triage and routing.

---

## ✨ Features
- 🧠 **AI-Powered Classification** — uses OpenAI API for zero-shot ticket labeling  
- ⚙️ **RESTful API** — single endpoint `/classify`  
- 🐳 **Docker Ready** — easily deployable as a standalone container  
- 💚 **Health Check** — simple `/health` route for monitoring  

---

## 🛠️ Technologies Used
- Python 3.10  
- Flask  
- Gunicorn  
- Docker  
- OpenAI API (GPT-4o-mini)

---

## 🚀 Quick Start

### 1️⃣ Clone the repo
```bash
git clone https://github.com/ArtemRivnyi/ai-ticket-classifier.git
cd ai-ticket-classifier
```

### 2️⃣ Set up environment
Create a file `.env`:
```env
OPENAI_API_KEY=sk-your-key-here
```

### 3️⃣ Build and run with Docker
```bash
docker build -t ai-ticket-classifier .
docker run --rm --env-file .env -p 5000:5000 ai-ticket-classifier
```

Then open [http://127.0.0.1:5000/health](http://127.0.0.1:5000/health) → should return:
```json
{"status": "ok"}
```

### 4️⃣ Send test request
```powershell
$body = '{"ticket":"I cannot connect to the VPN after Windows update."}'
Invoke-RestMethod -Uri http://127.0.0.1:5000/classify -Method Post -ContentType 'application/json' -Body $body
```
Response:
```json
{"category": "Network Issue"}
```

---

## 🧩 Example Categories

| Category | Example Ticket |
|-----------|----------------|
| **Network Issue** | “VPN not connecting”, “Wi-Fi drops constantly” |
| **Account Problem** | “Can’t log in”, “Password reset fails” |
| **Payment Issue** | “Refund request”, “Invoice missing” |
| **Feature Request** | “Add dark mode” |
| **Other** | Anything else |

---

## 🧠 Planned Improvements
- [ ] JSON Schema validation (Pydantic)
- [ ] Retry logic for OpenAI rate limits
- [ ] Add test suite and CI/CD workflow
- [ ] Online deployment (Render / Railway)
- [ ] Logging improvements

---

## 🧰 Maintainer
**Artem Rivnyi** — Junior Technical Support / DevOps Enthusiast  
📧 [artemrivnyi@outlook.com](mailto:artemrivnyi@outlook.com)  
🔗 [LinkedIn](https://www.linkedin.com/in/artem-rivnyi/)
