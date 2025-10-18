# 🤖 AI Ticket Classifier API

A lightweight AI-powered backend built with **Flask**, **OpenAI GPT-4o-mini**, and **Docker Compose**.
It classifies incoming support tickets into categories such as *Network Issue*, *Login Problem*, or *Payment Issue*.
Ideal for automating support triage in small tech teams or helpdesks.

---

## ✨ Features

* 🧠 **AI-Powered Classification** using OpenAI GPT models
* ⚙️ **RESTful API** with `/classify` endpoint
* 💚 **Health Check** at `/health`
* 🐳 **Docker & Docker Compose Ready** — deploy anywhere in seconds
* 🔁 **Automatic restart** and container health monitoring

---

## 🛠️ Technologies Used

* Python 3.10
* Flask
* Gunicorn
* Docker + Docker Compose
* OpenAI API (GPT-4o-mini)

---

## 🚀 Quick Start

### 1️⃣ Clone the repo

```bash
git clone https://github.com/ArtemRivnyi/ai-ticket-classifier.git
cd ai-ticket-classifier
```

### 2️⃣ Configure API key

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-key-here
```

### 3️⃣ Run with Docker Compose (recommended)

Build and start the service:

```bash
docker compose up --build
```

Stop the service:

```bash
docker compose down
```

### 4️⃣ Test the API

**Health check:**

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/health
```

**Classify a ticket:**

```powershell
$body = '{"ticket":"I cannot connect to the VPN"}'
Invoke-RestMethod -Uri http://127.0.0.1:5000/classify -Method Post -ContentType 'application/json' -Body $body
```

**Expected response:**

```json
{"category": "Network Issue"}
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

* JSON Schema validation (Pydantic)
* Retry logic for OpenAI rate limits
* GitHub Actions (CI/CD)
* Cloud deployment (Render / Railway)
* Structured logging

---

## 🧰 Maintainer

**Artem Rivnyi** — Junior Technical Support / DevOps Enthusiast
📧 [artemrivnyi@outlook.com](mailto:artemrivnyi@outlook.com)
🔗 [LinkedIn](https://www.linkedin.com/in/artemrivnyi)
