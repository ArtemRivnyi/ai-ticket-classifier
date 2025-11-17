import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
print(f"Testing API Key: {api_key[:20]}...")

genai.configure(api_key=api_key)

print("\n📋 Available models:")
print("-" * 50)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Display: {model.display_name}")
        print(f"   Description: {model.description[:100]}...")
        print()
