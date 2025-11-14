import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

load_dotenv()

# Настройка логгера для этого модуля
logger = logging.getLogger(__name__)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

def classify_ticket(ticket_text: str) -> str:
    """
    Classify a ticket using Gemini API with improved prompt
    Returns: category string
    """
    try:
        prompt = f"""You are an expert IT support ticket classifier. Your task is to categorize support tickets into specific categories based on their content.

CATEGORIES AND DEFINITIONS:

1. **Network Issue** - Problems related to connectivity, internet access, VPN, Wi-Fi, network speed, network configuration
   Examples: "Cannot connect to VPN", "Internet is slow", "Wi-Fi keeps disconnecting", "Cannot access network drive"

2. **Hardware Issue** - Problems with physical equipment like laptops, keyboards, monitors, printers, mice, cables
   Examples: "Laptop keyboard not working", "Monitor screen is blank", "Printer won't print", "Mouse is broken"

3. **Software Issue** - Problems with applications, software crashes, installation issues, software bugs
   Examples: "Microsoft Word keeps crashing", "Cannot install software", "Application freezing", "Software won't open"

4. **Account Problem** - Issues with user accounts, passwords, login, permissions, access rights
   Examples: "Cannot login to my account", "Forgot password", "Account is locked", "Need access to database"

5. **Payment Issue** - Problems related to billing, payments, invoices, subscriptions, charges
   Examples: "Was charged twice", "Cannot process payment", "Invoice is incorrect", "Subscription not working"

6. **Feature Request** - Requests for new features, enhancements, or improvements to existing systems
   Examples: "Can we add dark mode?", "Need bulk export feature", "Suggest improving search function"

7. **Other** - Tickets that don't fit into any of the above categories

INSTRUCTIONS:
- Read the ticket carefully
- Match it to the most appropriate category based on the definitions above
- Respond with ONLY the category name, nothing else
- If the ticket clearly matches multiple categories, choose the primary issue
- Be specific: prefer "Hardware Issue", "Software Issue", "Network Issue" over "Other" when applicable

TICKET TO CLASSIFY:
"{ticket_text}"

CATEGORY:"""

        model = genai.GenerativeModel('gemini-2.0-flash')
        
        generation_config = genai.types.GenerationConfig(
            temperature=0.1,  # Lower temperature for more consistent categorization
            max_output_tokens=30,
            top_p=0.95,
        )
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        category = response.text.strip()
        
        # Validate response is one of the expected categories
        valid_categories = [
            "Network Issue",
            "Hardware Issue", 
            "Software Issue",
            "Account Problem",
            "Payment Issue",
            "Feature Request",
            "Other"
        ]
        
        # Try to match the response to a valid category (case-insensitive)
        category_lower = category.lower()
        for valid_cat in valid_categories:
            if valid_cat.lower() in category_lower or category_lower in valid_cat.lower():
                logger.info(f"Classified ticket as: {valid_cat}")
                return valid_cat
        
        # If no match found, log warning and return Other
        logger.warning(f"Unexpected category from Gemini: {category}, defaulting to Other")
        return "Other"

    except google_exceptions.GoogleAPIError as e:
        logger.error(f"Gemini API error: {e}")
        return "Error"
    except Exception as e:
        logger.error(f"Unexpected error in classification: {e}")
        return "Error"