import pytest
from utils.rule_engine import RuleEngine


@pytest.fixture
def rule_engine():
    return RuleEngine()


def test_rule_engine_initialization(rule_engine):
    """Test that RuleEngine initializes with rules"""
    assert len(rule_engine.rules) > 0


def test_classify_billing_bug(rule_engine):
    """Test classification of Billing Bug"""
    text = "The invoice says I was charged twice for the same subscription"
    result = rule_engine.classify(text)
    assert result is not None
    assert result["category"] == "Billing Issue"  # Correct category name
    assert result["subcategory"] == "Invoice Mismatch"
    assert result["priority"] == "critical"  # Billing Issue has critical priority


def test_classify_authentication_issue(rule_engine):
    """Test classification of Authentication Issue"""
    text = "I cannot log in to my account, the button is greyed out"
    result = rule_engine.classify(text)
    assert result is not None
    assert result["category"] == "Authentication Issue"
    assert result["subcategory"] == "Login Failure"
    assert result["priority"] == "high"


def test_classify_critical_issue(rule_engine):
    """Test classification of Critical Issue"""
    text = "Production down! All users affected by system crash"
    result = rule_engine.classify(text)
    assert result is not None
    assert result["priority"] == "critical"


def test_classify_no_match(rule_engine):
    """Test classification with no match"""
    text = "Just saying hello"
    result = rule_engine.classify(text)
    assert result is None
