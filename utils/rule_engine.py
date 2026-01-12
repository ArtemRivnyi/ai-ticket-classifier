import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

VALID_CATEGORIES = [
    "Account Problem",
    "Authentication Issue",
    "Billing Issue",
    "Bug/Technical Issue",
    "Data / Reporting Issue",
    "Feature Request",
    "General Question",
    "Hardware Issue",
    "Integration Issue",
    "Mixed Issue",
    "Network Issue",
    "Notification Issue",
    "Security Incident",
    "Spam / Abuse",
    "Other",
]

SUBCATEGORIES = {
    "Authentication Issue": [
        "Login Failure",
        "2FA/MFA Issue",
        "Password Reset",
        "Session Expired",
        "Reset Link Expired",
    ],
    "Hardware Issue": [
        "Device Malfunction",
        "Battery/Power",
        "Connectivity (Hardware)",
        "Firmware",
    ],
    "Billing Issue": [
        "Invoice Mismatch",
        "UI/Backend Mismatch",
        "Webhook Failure",
        "Transaction Failed",
        "Refund Request",
        "Unrecognized Charge",
        "Double Charge",
    ],
    "Integration Issue": [
        "API Failure",
        "Webhook Error",
        "SSO/OAuth",
        "Third-party Service",
    ],
    "Notification Issue": ["Email Delivery", "Slack/SMS", "Partial Delivery"],
    "Network Issue": ["Connectivity Loss", "Latency/Slowness", "VPN Issue", "WiFi"],
    "Account Problem": ["Profile Update", "Settings", "Permissions"],
    "Bug/Technical Issue": ["Crash/Error", "Performance", "UI/UX Glitch"],
    "Security Incident": ["Unauthorized Access", "Data Breach", "Phishing"],
    "Feature Request": ["New Feature", "Improvement", "Configuration Change"],
    "General Question": ["How-to", "Documentation", "Pricing/Sales"],
    "Spam / Abuse": ["Spam", "Harassment"],
    "Mixed Issue": ["Multiple Issues"],
    "Other": ["Unclassified"],
}

CATEGORY_SYNONYMS = {
    "network": "Network Issue",
    "vpn issue": "Network Issue",
    "connectivity": "Network Issue",
    "latency": "Network Issue",
    "outage": "Network Issue",
    "wifi": "Network Issue",
    "account": "Account Problem",
    "profile": "Account Problem",
    "settings": "Account Problem",
    "login": "Authentication Issue",
    "password": "Authentication Issue",
    "2fa": "Authentication Issue",
    "otp": "Authentication Issue",
    "verification": "Authentication Issue",
    "mfa": "Authentication Issue",
    "billing": "Billing Issue",
    "payment": "Billing Issue",
    "charge": "Billing Issue",
    "charged": "Billing Issue",
    "refund": "Billing Issue",
    "invoice": "Billing Issue",
    "invoice mismatch": "Billing Issue",
    "billing bug": "Billing Issue",
    "ui payment": "Billing Issue",
    "processor mismatch": "Billing Issue",
    "idea": "Feature Request",
    "suggestion": "Feature Request",
    "roadmap": "Feature Request",
    "bug": "Bug/Technical Issue",
    "crash": "Bug/Technical Issue",
    "error": "Bug/Technical Issue",
    "exception": "Bug/Technical Issue",
    "hardware": "Hardware Issue",
    "printer": "Hardware Issue",
    "camera": "Hardware Issue",
    "sensor": "Hardware Issue",
    "battery": "Hardware Issue",
    "card reader": "Hardware Issue",
    "api": "Integration Issue",
    "webhook": "Integration Issue",
    "integration": "Integration Issue",
    "sdk": "Integration Issue",
    "oauth": "Integration Issue",
    "sso": "Integration Issue",
    "slack": "Notification Issue",
    "notification": "Notification Issue",
    "email": "Notification Issue",
    "sms": "Notification Issue",
    "alert": "Notification Issue",
    "security": "Security Incident",
    "breach": "Security Incident",
    "hacked": "Security Incident",
    "ransomware": "Security Incident",
    "compromised": "Security Incident",
    "phishing": "Security Incident",
    "report": "Data / Reporting Issue",
    "analytics": "Data / Reporting Issue",
    "analytics": "Data / Reporting Issue",
    "integration / api issue": "Integration Issue",
}

PRIORITY_MAP = {
    "Security Incident": "critical",
    "Mixed Issue": "critical",
    "Network Issue": "high",
    "Billing Issue": "critical",  # Default to critical for financial issues
    "Authentication Issue": "high",
    "Hardware Issue": "high",
    "Integration Issue": "high",  # Changed to high for Salesforce/API failures
    "Bug/Technical Issue": "medium",
    "Account Problem": "medium",
    "Data / Reporting Issue": "medium",
    "Notification Issue": "medium",
    "Spam / Abuse": "low",
    "Feature Request": "low",
    "General Question": "low",
    "Other": "medium",
}

# Specific subcategory priority overrides
SUBCATEGORY_PRIORITY_OVERRIDES = {
    ("Authentication Issue", "Reset Link Expired"): "medium",
    (
        "Hardware Issue",
        "Connectivity (Hardware)",
    ): "medium",  # Printer/USB usually medium
    ("Notification Issue", "Slack/SMS"): "medium",
    (
        "Billing Issue",
        "Refund Request",
    ): "high",  # Refunds are high but maybe not critical
    ("Billing Issue", "Transaction Failed"): "high",  # Failed transaction is high
    ("Billing Issue", "Unrecognized Charge"): "high",
    ("Billing Issue", "UI/Backend Mismatch"): "medium",
}

# CRITICAL priority keywords
# CRITICAL priority keywords
CRITICAL_KEYWORDS = [
    r"production down",
    r"server down",
    r"all users affected",
    r"can\'t work",
    r"losing money",
    r"complete outage",
    r"system crash",
    r"data loss",
    r"charged twice",
    r"invoice mismatch",
    r"wrong amount",
    r"security breach",
]

BLACKLIST_KEYWORDS = [
    r"free money",
    r"visit .*bitcoin",
    r"click here",
    r"phishing",
    r"buy now",
]

# Precedence order for resolving multiple matches
# Specific/Critical categories > Generic categories
CATEGORY_PRECEDENCE = [
    "Security Incident",
    "Billing Issue",
    "Hardware Issue",
    "Integration Issue",
    "Notification Issue",
    "Authentication Issue",
    "Account Problem",
    "Network Issue",
    "Feature Request",  # Moved before Bug/Technical Issue
    "Bug/Technical Issue",
    "Data / Reporting Issue",
    "General Question",
    "Spam / Abuse",
    "Mixed Issue",
    "Other",
]


def _compile_category_rules() -> List[Dict]:
    return [
        {
            "category": "Billing Issue",
            "subcategory": "Invoice Mismatch",
            "patterns": [
                r"invoice (mismatch|says)",
                r"invoice.*\$\d+.*charged.*\$\d+",
                r"charged twice.*invoice",
                r"same invoice.*twice",
                r"tax.*wrong",
                r"tax.*calculation",
            ],
        },
        {
            "category": "Billing Issue",
            "subcategory": "Webhook Failure",
            "patterns": [
                r"processor (did not confirm|charged)",
                r"webhook (shows|mismatch)",
                r"stripe.*failed",
            ],
        },
        {
            "category": "Billing Issue",
            "subcategory": "UI/Backend Mismatch",
            "patterns": [
                r"dashboard.*paid.*dunning",
                r"says.*paid.*dunning",
                r"ui shows paid",
                r"logs show unpaid",
                r"dashboard shows paid.*backend",
                r"backend.*unpaid",
                r"status.*active.*features.*locked",
                r"subscription.*active.*locked",
                r"update.*payment.*method",
                r"card.*expired",
            ],
        },
        {
            "category": "Feature Request",
            "subcategory": "New Feature",
            "patterns": [
                r"add animation",
                r"feature request",
                r"new feature",
                r"need an api",
                r"create an api",
                r"\badd dark mode",
                r"\badd.*dark mode",
                r"would be great",
                r"nice (to have|if)",
                r"could you add",
            ],
        },
        {
            "category": "Feature Request",
            "subcategory": "Improvement",
            "patterns": [
                r"would be nice",
                r"nice to have",
                r"would like",
                r"suggestion",
                r"improvement",
                r"enhancement",
                r"can you add",
                r"make the.*collapsible",
                r"export to",
            ],
        },
        {
            "category": "Hardware Issue",
            "subcategory": "Battery/Power",
            "patterns": [
                r"\bbattery\b",
                r"\bac\b",
                r"drains in",
            ],
        },
        # Firmware MUST come before Device Malfunction to catch "device firmware update failed"
        {
            "category": "Hardware Issue",
            "subcategory": "Firmware",
            "patterns": [
                r"firmware.*update.*failed",
                r"firmware.*failed",
                r"firmware update",
            ],
        },
        {
            "category": "Hardware Issue",
            "subcategory": "Device Malfunction",
            "patterns": [
                r"\bcamera\b",
                r"\bsensor\b",
                r"\bprinter\b",
                r"card reader",
                r"\bdevice\b",
                r"jamming",
                r"not detecting",
                r"stopped working",
                r"flickering",
            ],
        },
        {
            "category": "Hardware Issue",
            "subcategory": "Connectivity (Hardware)",
            "patterns": [
                r"\brouter\b",
                r"usb cable",
            ],
        },
        {
            "category": "Integration Issue",
            "subcategory": "Webhook Error",
            "patterns": [
                r"webhook",
                r"callback",
            ],
        },
        {
            "category": "Integration Issue",
            "subcategory": "API Failure",
            "patterns": [
                r"api.*error",
                r"api.*fail",
                r"api.*timeout",
                r"\bsdk\b",
                r"api.*not responding",
            ],
        },
        # Authentication Login Failure MUST come before SSO/OAuth to catch "sso login button"
        {
            "category": "Authentication Issue",
            "subcategory": "Login Failure",
            "patterns": [
                r"cannot log in",
                r"can't log in",
                r"failed login",
                r"login button.*greyed",
                r"locked out",
                r"sso.*button",
                r"sso.*login.*button",
            ],
        },
        {
            "category": "Integration Issue",
            "subcategory": "SSO/OAuth",
            "patterns": [
                r"auth token",
                r"azure ad",
                r"oauth",
                r"invalid_grant",
            ],
        },
        {
            "category": "Integration Issue",
            "subcategory": "Third-party Service",
            "patterns": [
                r"integration",
                r"slack.*not coming",
                r"slack.*notifications",
                r"salesforce",
                r"hubspot",
                r"jira",
                r"third-party",
                r"external service",
            ],
        },
        {
            "category": "Notification Issue",
            "subcategory": "Email Delivery",
            "patterns": [
                r"email.*not delivered",
                r"didn\'t receive.*email",
                r"email.*spam",
                r"email.*blank",
            ],
        },
        {
            "category": "Notification Issue",
            "subcategory": "Partial Delivery",
            "patterns": [
                r"half.*team",
                r"some users",
                r"partial.*delivery",
                r"delayed.*hours",
                r"notifications.*delayed",
                r"notifications.*some",
            ],
        },
        {
            "category": "Notification Issue",
            "subcategory": "Slack/SMS",
            "patterns": [
                r"slack.*alerts",
                r"\bsms\b",
                r"\balert\b",
                r"push message",
                r"slack integration",
                r"slack.*notification",
            ],
        },
        {
            "category": "Notification Issue",
            "subcategory": None,  # General
            "patterns": [
                r"notification",
            ],
        },
        {
            "category": "Authentication Issue",
            "subcategory": "2FA/MFA Issue",
            "patterns": [
                r"invalid code",
                r"verification (code|failed)",
                r"\b2fa\b",
                r"\bmfa\b",
                r"\botp\b",
                r"verification code",
                r"authenticator",
                r"two-factor",
            ],
        },
        {
            "category": "Authentication Issue",
            "subcategory": "Login Failure",
            "patterns": [
                r"cannot log in",
                r"can't log in",
                r"failed login",
                r"login button.*greyed",
                r"locked out",
                r"sso.*button",
            ],
        },
        {
            "category": "Authentication Issue",
            "subcategory": "Session Expired",
            "patterns": [
                r"session expired",
                r"session timeout",
                r"logged out",
            ],
        },
        {
            "category": "Authentication Issue",
            "subcategory": "Reset Link Expired",
            "patterns": [
                r"link.*expired",
                r"expired.*link",
                r"token.*expired",
            ],
        },
        {
            "category": "Authentication Issue",
            "subcategory": "Password Reset",
            "patterns": [
                r"reset link",
                r"password reset",
                r"forgot.*password",
            ],
        },
        {
            "category": "Billing Issue",
            "subcategory": "Double Charge",
            "patterns": [
                r"charged twice",
                r"double charge",
                r"duplicate charge",
                r"billed twice",
                r"same invoice.*twice",
            ],
        },
        {
            "category": "Billing Issue",
            "subcategory": "Refund Request",
            "patterns": [
                r"refund",
                r"chargeback",
            ],
        },
        {
            "category": "Billing Issue",
            "subcategory": "Transaction Failed",
            "patterns": [
                r"transaction failed",
                r"payment failed",
                r"payment completed",  # Context usually implies issue despite "completed"
                r"insufficient funds",
                r"card expired",
                r"payment.*error",
                r"transaction.*error",
                r"credit card.*expired",
            ],
        },
        {
            "category": "Billing Issue",
            "subcategory": "Unrecognized Charge",
            "patterns": [
                r"\bcharged\b",
                r"unauthorized payment",
                r"unknown charge",
                r"billing error",
                r"wrong billing",
                r"incorrect charge",
            ],
        },
        {
            "category": "Security Incident",
            "subcategory": "Data Breach",
            "patterns": [
                r"breach",
                r"data leak",
            ],
        },
        {
            "category": "Security Incident",
            "subcategory": "Unauthorized Access",
            "patterns": [
                r"hacked",
                r"compromised",
                r"intrusion",
            ],
        },
        {
            "category": "Bug/Technical Issue",
            "subcategory": "Performance",
            "patterns": [
                r"slow",
                r"takes.*seconds",
                r"loading",
                r"latency",
            ],
        },
        {
            "category": "Bug/Technical Issue",
            "subcategory": "UI/UX Glitch",
            "patterns": [
                r"misaligned",
                r"glitch",
                r"overlap",
                r"css",
                r"style",
                r"cosmetic issue",
                r"button alignment",
                r"minor (issue|bug)",
            ],
        },
        {
            "category": "Bug/Technical Issue",
            "subcategory": "Crash/Error",
            "patterns": [
                r"crash",
                r"error",
                r"exception",
                r"traceback",
                r"undefined",
                r"not a function",
                r"empty",  # Search results empty
                r"null pointer",
                r"javascript error",
                r"stacktrace",
                r"crash when",
                r"bug",
            ],
        },
        {
            "category": "Network Issue",
            "subcategory": "Connectivity Loss",
            "patterns": [
                r"cannot connect",
                r"connection timeout",
                r"\bwifi\b",
                r"connection dropping",
                r"keeps dropping",
                r"\binternet\b",
            ],
        },
        {
            "category": "Network Issue",
            "subcategory": "Latency/Slowness",
            "patterns": [
                r"latency",
                r"\bnetwork\b",
                r"connectivity",
            ],
        },
        {
            "category": "Account Problem",
            "subcategory": "Profile Update",
            "patterns": [
                r"profile update",
                r"wrong email",
                r"change.*email",
                r"wrong name",
                r"update.*profile",
            ],
        },
        {
            "category": "Account Problem",
            "subcategory": "Settings",
            "patterns": [
                r"account settings",
                r"delete my account",
                r"upgrade.*plan",
            ],
        },
        {
            "category": "Account Problem",
            "subcategory": "Permissions",
            "patterns": [
                r"access.*page",
                r"permission",
                r"admin access",
            ],
        },
        {
            "category": "Account Problem",
            "subcategory": None,
            "patterns": [
                r"phishing",  # Context dependent, but kept from original
                r"crypto",
                r"promo",
            ],
        },
        {
            "category": "General Question",
            "subcategory": "How-to",
            "patterns": [
                r"how do i",
                r"can you explain",
            ],
        },
        {
            "category": "General Question",
            "subcategory": None,
            "patterns": [
                r"general question",
            ],
        },
        {
            "category": "General Question",
            "subcategory": "Documentation",
            "patterns": [
                r"documentation",
                r"guide",
                r"manual",
                r"where can i find",
            ],
        },
        {
            "category": "Bug/Technical Issue",
            "subcategory": "Crash/Error",
            "patterns": [
                r"freezes",
                r"frozen",
                r"stuck",
                r"not finding",
                r"search function",
                r"incorrect data",
                r"wrong data",
            ],
        },
        {
            "category": "Authentication Issue",
            "subcategory": "Account Locked",
            "patterns": [
                r"locked",
                r"account.*locked",
                r"suspicious activity",
            ],
        },
        {
            "category": "Billing Issue",
            "subcategory": "Payment Method",
            "patterns": [
                r"credit card",
                r"update.*card",
                r"payment method",
            ],
        },
        {
            "category": "Billing Issue",
            "subcategory": "Subscription Management",
            "patterns": [
                r"cancel.*subscription",
                r"unsubscribe",
                r"stop.*billing",
            ],
        },
        {
            "category": "Hardware Issue",
            "subcategory": "Device Malfunction",
            "patterns": [
                r"keyboard",
                r"mouse",
                r"(?<!splash )screen",  # Avoid matching "splash screen"
                r"monitor",
                r"laptop",
                r"sticking",
            ],
        },
        {
            "category": "Bug/Technical Issue",
            "subcategory": "Crash/Error",
            "patterns": [
                r"freezes",
                r"frozen",
                r"stuck",
                r"not finding",
                r"search function",
                r"incorrect data",
                r"wrong data",
                r"500 internal server error",
                r"splash screen",
            ],
        },
        {
            "category": "Network Issue",
            "subcategory": "Connectivity Loss",
            "patterns": [
                r"unstable",
                r"dropping",
                r"disconnecting",
            ],
        },
        {
            "category": "Feature Request",
            "subcategory": "New Feature",
            "patterns": [
                r"is there a way to",
                r"can i integrate",
                r"support for",
            ],
        },
        {
            "category": "General Question",
            "subcategory": None,
            "patterns": [
                r"question about",
                r"inquiry",
            ],
        },
    ]


class RuleEngine:
    """Deterministic regex/keyword rules for obvious cases."""

    def __init__(self):
        self.rules = _compile_category_rules()

    def classify(self, ticket_text: str) -> Optional[Dict]:
        text = ticket_text.lower()
        matches = []

        # Debug logging
        logger.info(f"🔍 Rule Engine processing: '{text[:50]}...'")

        # Find all matching categories
        for i, rule in enumerate(self.rules):
            if any(re.search(pattern, text) for pattern in rule["patterns"]):
                matches.append(
                    {
                        "index": i,
                        "category": rule["category"],
                        "subcategory": rule.get("subcategory"),
                    }
                )
                logger.info(
                    f"✅ Match found: {rule['category']} -> {rule.get('subcategory')}"
                )

        if not matches:
            logger.info("❌ No rules matched")
            return None

        # Special case: If Mixed Issue explicit pattern matches, it takes precedence
        mixed_match = next((m for m in matches if m["category"] == "Mixed Issue"), None)
        if mixed_match:
            logger.info(f"🔀 Mixed Issue detected, overriding other matches")
            return {
                "category": "Mixed Issue",
                "subcategory": mixed_match["subcategory"] or "Multiple Issues",
                "confidence": 0.80,
                "priority": "critical",  # Multiple issues = critical
                "provider": "rule_engine",
            }

        # Select the best category based on precedence
        # Sort by:
        # 1. Category Precedence (lower index = higher priority)
        # 2. Rule Index (lower index = more specific rule, assuming rules are ordered)

        def sort_key(match):
            try:
                cat_priority = CATEGORY_PRECEDENCE.index(match["category"])
            except ValueError:
                cat_priority = float("inf")
            return (cat_priority, match["index"])

        matches.sort(key=sort_key)
        best_match = matches[0]

        # Find the specific pattern that matched
        matched_pattern = None
        rule = self.rules[best_match["index"]]
        for pattern in rule["patterns"]:
            if re.search(pattern, text):
                matched_pattern = pattern
                break

        # Determine priority
        priority = PRIORITY_MAP.get(best_match["category"], "medium")

        # Check for subcategory overrides
        if (
            best_match["category"],
            best_match["subcategory"],
        ) in SUBCATEGORY_PRIORITY_OVERRIDES:
            priority = SUBCATEGORY_PRIORITY_OVERRIDES[
                (best_match["category"], best_match["subcategory"])
            ]

        # Check for CRITICAL keywords
        if any(re.search(pattern, text) for pattern in CRITICAL_KEYWORDS):
            priority = "critical"

        return {
            "category": best_match["category"],
            "subcategory": best_match["subcategory"],
            "confidence": 0.80,  # Lowered to allow more Gemini usage
            "priority": priority,
            "provider": "rule_engine",
            "matched_pattern": matched_pattern,
        }
