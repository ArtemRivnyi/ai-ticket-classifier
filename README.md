# 🤖 AI Ticket Classifier API (Flask + OpenAI)

An automated backend service built with **Flask** and **OpenAI's GPT-4o-mini** to instantly classify incoming support tickets into predefined categories. Ideal for triaging and routing customer service requests.

## ✨ Features

* **RESTful API:** Simple POST endpoint `/classify`.
* **AI-Powered Triage:** Uses a fast and cost-effective OpenAI model for classification.
* **Scalable (Microservice):** Easy to deploy as a standalone service.

---

## 🚀 Quick Start

### 🧱 1. Setup

1. Clone the repository:

```bash
git clone https://github.com/YourUsername/ai-ticket-classifier
cd ai-ticket-classifier
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
.\venv\Scripts\activate   # For Windows PowerShell/CMD
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### 🔑 2. API Key Configuration

Create a file named **`.env`** in the root directory and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-secret-key-here
```

> ⚠️ Secure your key and **never** commit the `.env` file to Git. The `.gitignore` file should handle this.

### 🧪 3. Run the Server

Start the Flask application:

```bash
python app.py
```

### 🌐 4. Test the API (PowerShell)

With the server running, send a test request from a new terminal:

```powershell
$body = '{"ticket": "I cannot connect to the VPN after the Windows update."}'
Invoke-RestMethod -Uri http://127.0.0.1:5000/classify -Method Post -ContentType 'application/json' -Body $body
```

**Expected Successful Output:**

```text
category
--------
Network Issue
```

---

## 📈 Project Status: Classification Model

This project currently uses a Zero-Shot Classification approach (relying on the LLM's inherent knowledge). This offers great flexibility but limits performance on highly specialized, internal data.

### Current State

| Metric                 | Status (English)             | Notes                                                               |
| ---------------------- | ---------------------------- | ------------------------------------------------------------------- |
| Accuracy (Estimated)   | High (for common categories) | LLMs are generally reliable for basic categorization tasks.         |
| Edge Cases / Ambiguity | Medium                       | Classification might fail or return "Other" for specialized jargon. |
| Cost                   | Very Low                     | Utilizes gpt-4o-mini, one of OpenAI's most cost-effective models.   |

### Example Categories

| Category        | Example Tickets                             |
| --------------- | ------------------------------------------- |
| Network Issue   | "Wi-Fi not connecting", "VPN error"         |
| Account Problem | "Can't login", "Password reset needed"      |
| Payment Issue   | "Invoice not received", "Refund request"    |
| Feature Request | "Add dark mode", "New report format needed" |
| Other           | Anything that doesn't fit above categories  |

---

## 🛠️ Planned Improvements

* **Strict Output Enforcement (JSON Schema):** Implement a strict JSON output format from the LLM using Pydantic or OpenAI's Response Format to prevent unparseable text.
* **Add Robust Error Handling:** Implement automatic retries for transient errors (like RateLimitError: 429) before failing the request.
* **Domain-Specific Fine-Tuning:** Collect labeled historical tickets to fine-tune a model for internal data.
* **Benchmarking and Metrics:** Set up a testing suite with real-world examples to measure and report Precision, Recall, and F1-Score.
