"""
Helpers for bridging Zendesk webhooks with the AI Ticket Classifier.

The adapter converts inbound webhook payloads into prompts, attaches
recommended tags/priority, and prepares update instructions for Zendesk.
"""

from __future__ import annotations

from typing import Dict, List


class ZendeskAdapter:
    """Simple mapper between classifier output and Zendesk ticket fields."""

    CATEGORY_TAGS = {
        'Network Issue': ['network_issue', 'vpn'],
        'Account Problem': ['account', 'login'],
        'Payment Issue': ['billing', 'payment'],
        'Feature Request': ['feature_request'],
        'Spam / Abuse': ['abuse', 'spam'],
        'Other': ['triage_needed'],
    }

    CATEGORY_GROUP = {
        'Network Issue': 'tech_support',
        'Account Problem': 'account_support',
        'Payment Issue': 'billing',
        'Feature Request': 'product',
        'Spam / Abuse': 'abuse',
        'Other': 'triage',
    }

    @classmethod
    def compose_ticket_text(cls, subject: str, description: str) -> str:
        """Combine subject + description for classification."""
        subject = subject.strip() if subject else ''
        description = description.strip() if description else ''
        return f"{subject}\n\n{description}".strip()

    @classmethod
    def build_tags(cls, category: str) -> List[str]:
        """Return recommended Zendesk tags for a category."""
        default = ['ai_classifier']
        return default + cls.CATEGORY_TAGS.get(category, ['triage_needed'])

    @classmethod
    def build_update(cls, payload: Dict, classification: Dict) -> Dict:
        """
        Build a Zendesk-style update payload describing next actions.

        Args:
            payload: validated webhook payload (dict-like).
            classification: dict from classifier (category, confidence, etc.).
        """
        category = classification.get('category', 'Other')
        tags = cls.build_tags(category)
        group = cls.CATEGORY_GROUP.get(category, 'triage')

        comment = (
            f"[AI] Classified as {category} "
            f"(confidence {classification.get('confidence', 0):.2f})."
        )

        return {
            'ticket_id': payload['ticket_id'],
            'group': group,
            'priority': classification.get('priority', 'medium'),
            'tags': tags,
            'public_comment': comment,
            'metadata': classification,
        }

