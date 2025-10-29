# 🤖 AI Ticket Classifier (OpenAI API Version)

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AI Ticket Classifier** is a lightweight, AI-powered backend built with **Flask**, **OpenAI GPT-4o-mini**, and **Docker Compose**. It automatically classifies incoming support tickets into categories such as _Network Issue_, _Account Problem_, or _Payment Issue_. Ideal for small tech teams, helpdesks, or e-commerce support operations seeking efficient ticket management.

## 📝 Table of Contents

* [✨ Features](#-features)
* [🛠️ Technologies Used](#️-technologies-used)
* [🚀 Quick Start](#-quick-start)
  * [1️⃣ Clone the Repository](#1️⃣-clone-the-repository)
  * [2️⃣ Configure API Key](#2️⃣-configure-api-key)
  * [3️⃣ Run with Docker Compose](#3️⃣-run-with-docker-compose)
  * [4️⃣ Test the API](#4️⃣-test-the-api)
* [🧪 Testing](#-testing)
* [🔧 Development](#-development)
* [🧩 Example Categories](#-example-categories)
* [📊 CI/CD Status](#-cicd-status)
* [🧠 Planned Improvements](#-planned-improvements)
* [📄 License](#-license)
* [🧰 Maintainer](#-maintainer)


## ✨ Features

*   🧠 **AI-Powered Classification**: Leverages the advanced capabilities of OpenAI GPT-4o-mini for accurate and efficient ticket categorization.
*   ⚙️ **RESTful API**: Provides well-defined `/api/v1/classify` and `/api/v1/health` endpoints for seamless integration and monitoring.
*   🐳 **Docker & Docker Compose Ready**: Facilitates rapid deployment across various environments, enabling setup in mere seconds.
*   🔁 **Automated Resilience**: Includes automatic restart mechanisms and container health monitoring to ensure continuous service availability.
*   💡 **Extensible Design**: Engineered for easy expansion with new classification categories and support for multiple languages.
*   ✅ **CI/CD Ready**: Integrated with GitHub Actions for automated testing and deployment workflows.

## 🛠️ Technologies Used

The project is built upon a robust stack of modern technologies:

*   **Python**: Version 3.10+ for core application logic.
*   **Flask**: A micro web framework for building the RESTful API.
*   **Gunicorn**: A Python WSGI HTTP Server for UNIX, used for production deployments.
*   **Docker & Docker Compose**: For containerization and orchestration, ensuring consistent environments.
*   **OpenAI API**: Specifically `GPT-4o-mini` for AI-powered text classification.
*   **GitHub Actions**: For Continuous Integration and Continuous Deployment (CI/CD).
*   **Pytest**: A powerful testing framework for Python.

## 🚀 Quick Start

Follow these steps to get the AI Ticket Classifier up and running quickly:

### 1️⃣ Clone the Repository

Begin by cloning the project repository to your local machine:

```shell
git clone https://github.com/ArtemRivnyi/ai-ticket-classifier.git
cd ai-ticket-classifier
```

### 2️⃣ Configure API Key

Create a `.env` file in the root directory of the project and add your OpenAI API key:

```dotenv
OPENAI_API_KEY=sk-your-openai-api-key-here
```

Obtain your API key from [OpenAI Platform]().

### 3️⃣ Run with Docker Compose

Build and start the service using Docker Compose:

```shell
docker compose up --build
```

To stop the service, execute:

```shell
docker compose down
```

### 4️⃣ Test the API

Verify the deployment and functionality of the API:

#### Health Check

```shell
curl http://127.0.0.1:5000/api/v1/health
```

#### Classify a Ticket

Send a POST request to the classify endpoint with a sample ticket:

```shell
curl -X POST http://127.0.0.1:5000/api/v1/classify \
-H "Content-Type: application/json" \
-d '{"ticket":"I cannot connect to the VPN"}'
```

**Expected Response:**

```json
{
  "category": "Network Issue",
  "suggested_response": "Please check your VPN connection and try again..."
}
```

## 🧪 Testing

Run the test suite to ensure everything is working as expected:

```shell
# Install test dependencies
pip install pytest

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_app.py -v
```

## 🔧 Development

For local development without Docker:

```shell
pip install -r requirements.txt
python app.py
```

Running tests during development:

```shell
python -m pytest tests/ -v
```

Code quality checks:

```shell
pip install flake8 pylint
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
pylint app.py classify.py tests/
```

## 🧩 Example Categories

This table illustrates typical ticket categories and corresponding examples:

| Category | Example Ticket |
| :-- | :-- |
| Network Issue | "VPN not connecting", "Wi-Fi drops constantly" |
| Account Problem | "Can't log in", "Password reset fails" |
| Payment Issue | "Refund request", "Invoice missing" |
| Feature Request | "Add dark mode" |
| Other | Any other unlisted issue |

## 📊 CI/CD Status

This project uses GitHub Actions for continuous integration, ensuring code quality and reliability:

*   ✅ Automated testing on every push
*   ✅ Docker image building and testing
*   ✅ Security scanning
*   ✅ Code quality checks

## 🧠 Planned Improvements

Future enhancements are envisioned to further improve the classifier's robustness and feature set:

*   **JSON Schema Validation**: Implementation of Pydantic for robust request and response validation.
*   **Retry Logic**: Introduction of retry mechanisms to handle API rate limits gracefully.
*   **Enhanced Error Handling**: Improved error management for more resilient operations.
*   **Cloud Deployment**: Guides and configurations for deployment on platforms like Render, Railway, or AWS.
*   **Structured Logging and Metrics**: Enhanced logging for better observability and performance monitoring.
*   **Multilingual Ticket Support**: Expansion to classify tickets in multiple languages.
*   **Web Dashboard**: Development of a web interface for ticket review and knowledge base management.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🧰 Maintainer

**Artem Rivnyi** — Junior Technical Support / DevOps Enthusiast

* 📧 [artemrivnyi@outlook.com](mailto:artemrivnyi@outlook.com)  
* 🔗 [LinkedIn](https://www.linkedin.com/in/artem-rivnyi/)  
* 🌐 [Personal Projects](https://personal-page-devops.onrender.com/)  
* 💻 [GitHub](https://github.com/ArtemRivnyi)
