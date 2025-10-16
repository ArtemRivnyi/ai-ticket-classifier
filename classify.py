import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_ticket(ticket_text: str) -> str:
    prompt = f"""
    You are a tech support assistant. 
    Classify the following ticket into ONE of the categories:
    - Network Issue
    - Software Bug
    - Login/Access Problem
    - Payment/Billing Issue
    - Other

    Ticket: "{ticket_text}"
    Reply only with the category name.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()
