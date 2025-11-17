import google.generativeai as genai
import os
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

logger = logging.getLogger(__name__)

class GeminiClassifier:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        
        genai.configure(api_key=api_key)
        
        # Try different models
        try:
            self.model = genai.GenerativeModel('models/gemini-1.5-pro')
            logger.info("Using gemini-1.5-pro")
        except:
            try:
                self.model = genai.GenerativeModel('models/gemini-pro')
                logger.info("Using gemini-pro")
            except:
                # Fallback
                self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
                logger.info("Using gemini-1.5-flash-latest")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    def classify(self, ticket_text):
        """Classify with retry logic"""
        try:
            prompt = f"""Classify this support ticket into ONE category:
- Network Issue
- Account Problem  
- Payment Issue
- Feature Request
- Other

Ticket: "{ticket_text}"

Return ONLY the category name, nothing else."""

            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.1,
                    'top_p': 1,
                    'top_k': 1,
                    'max_output_tokens': 50,
                }
            )
            
            category = response.text.strip()
            
            logger.info(f"Classification successful: {category}")
            
            return {
                'category': category,
                'confidence': 'high',
                'provider': 'gemini'
            }
            
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            raise
