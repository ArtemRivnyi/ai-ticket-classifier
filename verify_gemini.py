import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key present: {bool(api_key)}")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content("Hello")
        print(f"Gemini Response: {response.text}")
    except Exception as e:
        print(f"Gemini Error: {e}")
else:
    print("No API Key found")
