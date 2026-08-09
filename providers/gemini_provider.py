import google.generativeai as genai
import os
import json
import re
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import logging
from google.api_core import exceptions as google_exceptions
from utils.prompt_formatter import format_classification_prompt

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    def __init__(self, provider: str, retry_after: int = 60):
        self.provider = provider
        self.retry_after = retry_after
        super().__init__(f"{provider} rate limit exceeded. Retry after {retry_after}s")


class GeminiClassifier:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")

        genai.configure(api_key=api_key)

        # Try active Gemini models (2.5-flash primary, with fallbacks)
        models_to_try = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-flash-latest",
        ]
        self.model = None
        for m_name in models_to_try:
            try:
                self.model = genai.GenerativeModel(m_name)
                logger.info(f"Using {m_name}")
                break
            except Exception as e:
                logger.warning(f"Failed to init model {m_name}: {e}")

        if not self.model:
            self.model = genai.GenerativeModel("gemini-2.5-flash")

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        retry=retry_if_exception_type((Exception,)),
    )
    def classify(self, ticket_text: str, extra_examples: str = "") -> dict:
        """Classify with retry logic and comprehensive prompt"""
        result_text = ""
        try:
            prompt = format_classification_prompt(
                ticket_text, provider="gemini", extra_examples=extra_examples
            )

            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.1,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 500,
                },
            )

            result_text = response.text.strip()

            # Extract JSON from markdown code blocks if present
            json_match = re.search(
                r"```(?:json)?\s*(\{.*?\})\s*```", result_text, re.DOTALL
            )
            if json_match:
                result_text = json_match.group(1)

            result = json.loads(result_text)

            logger.info(
                f"Gemini classification: {result.get('category')} > {result.get('subcategory')}"
            )

            return {
                "category": result.get("category", "Other"),
                "subcategory": result.get("subcategory", "Unclassified"),
                "confidence": result.get("confidence", 0.85),
                "provider": "gemini",
            }

        except google_exceptions.ResourceExhausted as e:
            logger.error(f"⚠️ Gemini rate limit exceeded")
            raise RateLimitError("Gemini", retry_after=60)

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}, response: {result_text}")
            # Fallback: try to extract category from text
            return {
                "category": "Other",
                "subcategory": "Unclassified",
                "confidence": 0.5,
                "provider": "gemini",
            }
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            raise
