
import pytest
from utils.rule_engine import RuleEngine

@pytest.fixture
def rule_engine():
    return RuleEngine()

def test_classify_invoice_request(rule_engine):
    """Test that requesting an invoice is NOT a Payment Issue"""
    text = "I need a copy of my invoice"
    result = rule_engine.classify(text)
    # Should NOT match Payment Issue rules, should fall through to AI (return None from rule engine)
    # OR match a new 'General Question' rule if we added one (we haven't yet, so None is expected)
    assert result is None or result['category'] != 'Payment Issue'

def test_classify_billing_history(rule_engine):
    """Test that asking for billing history is NOT a Payment Issue"""
    text = "Where can I find my billing history?"
    result = rule_engine.classify(text)
    assert result is None or result['category'] != 'Payment Issue'

def test_classify_general_billing_question(rule_engine):
    """Test that general billing questions are NOT Payment Issues"""
    text = "I have a question about billing"
    result = rule_engine.classify(text)
    assert result is None or result['category'] != 'Payment Issue'

def test_classify_actual_billing_issue(rule_engine):
    """Test that actual billing issues ARE still caught"""
    text = "I was charged twice for the same invoice"
    result = rule_engine.classify(text)
    assert result is not None
    assert result['category'] == 'Payment Issue' or result['category'] == 'Billing Bug'

def test_classify_unrecognized_charge_specific(rule_engine):
    """Test that specific unrecognized charge patterns still work"""
    text = "There is an unknown charge on my card"
    result = rule_engine.classify(text)
    assert result is not None
    assert result['category'] == 'Payment Issue'
    assert result['subcategory'] == 'Unrecognized Charge'
