import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY not found")
    exit(1)

genai.configure(api_key=api_key)

print("Available models:")
for model in genai.list_models():
    print(f"- {model.name}")
    if 'generateContent' in model.supported_generation_methods:
        print(f"  Supports generateContent: Yes")
    else:
        print(f"  Supports generateContent: No")