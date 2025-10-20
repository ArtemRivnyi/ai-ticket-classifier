import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

def classify_ticket(ticket_text: str) -> str:
    """
    Classify a ticket using Gemini API
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

        model = genai.GenerativeModel('gemini-2.0-flash')
        
        generation_config = genai.types.GenerationConfig(
            temperature=0.3,
            max_output_tokens=20,
        )
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        category = response.text.strip()
        return category

    except google_exceptions.GoogleAPIError as e:
        print(f"[GeminiAPIError] {e}")
        return "Error"
    except Exception as e:
        print(f"[GeneralError] {e}")
        return "Error"