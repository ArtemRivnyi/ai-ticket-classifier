import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 🔥 Загружает переменные из .env

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def classify_ticket(ticket_text: str) -> str:
    """
    Classify a ticket using OpenAI API
    Returns: category string
    """
    try:
        prompt = f"""
        You are a support ticket classifier. Categorize the following ticket:
        "{ticket_text}"
        into one of these categories:
        - Network Issue
        - Account Problem
        - Payment Issue
        - Feature Request
        - Other
        Respond ONLY with the category name.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=20,
            timeout=10
        )

        category = response.choices[0].message.content.strip()
        return category

    except OpenAIError as e:
        print(f"[OpenAIError] {e}")
        return "Error"
    except Exception as e:
        print(f"[GeneralError] {e}")
        return "Error"
