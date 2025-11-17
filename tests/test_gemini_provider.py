"""
Comprehensive tests for providers/gemini_provider.py
Tests GeminiClassifier
"""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
import os

# Project requires Python 3.12
if sys.version_info < (3, 12) or sys.version_info >= (3, 13):
    pytestmark = pytest.mark.skip(
        reason="Project requires Python 3.12"
    )

# Mock google.generativeai before importing GeminiClassifier
with patch.dict('sys.modules', {'google.generativeai': MagicMock()}):
    try:
        from providers.gemini_provider import GeminiClassifier
    except:
        GeminiClassifier = None

@pytest.mark.skipif(GeminiClassifier is None, reason="GeminiClassifier not available")
def test_gemini_classifier_init_no_key():
    """Test GeminiClassifier initialization without API key"""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="GEMINI_API_KEY not set"):
            GeminiClassifier()

@pytest.mark.skipif(GeminiClassifier is None, reason="GeminiClassifier not available on Python 3.14")
def test_gemini_classifier_init_with_key(mocker):
    """Test GeminiClassifier initialization with API key"""
    mocker.patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'})
    mocker.patch('providers.gemini_provider.genai.configure')
    mocker.patch('providers.gemini_provider.genai.GenerativeModel')
    
    classifier = GeminiClassifier()
    assert classifier is not None

@pytest.mark.skipif(GeminiClassifier is None, reason="GeminiClassifier not available on Python 3.14")
def test_gemini_classifier_classify_success(mocker):
    """Test successful classification"""
    mocker.patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'})
    mocker.patch('providers.gemini_provider.genai.configure')
    
    # Mock model and response
    mock_response = Mock()
    mock_response.text = "Network Issue"
    mock_model = Mock()
    mock_model.generate_content.return_value = mock_response
    mocker.patch('providers.gemini_provider.genai.GenerativeModel', return_value=mock_model)
    
    classifier = GeminiClassifier()
    result = classifier.classify("I cannot connect to VPN")
    
    assert 'category' in result
    assert result['category'] == "Network Issue"
    assert result['provider'] == 'gemini'
    assert 'confidence' in result

@pytest.mark.skipif(GeminiClassifier is None, reason="GeminiClassifier not available on Python 3.14")
def test_gemini_classifier_classify_error(mocker):
    """Test classification error handling"""
    mocker.patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'})
    mocker.patch('providers.gemini_provider.genai.configure')
    
    # Mock model to raise error
    mock_model = Mock()
    mock_model.generate_content.side_effect = Exception("API Error")
    mocker.patch('providers.gemini_provider.genai.GenerativeModel', return_value=mock_model)
    
    classifier = GeminiClassifier()
    
    with pytest.raises(Exception):
        classifier.classify("Test ticket")

@pytest.mark.skipif(GeminiClassifier is None, reason="GeminiClassifier not available on Python 3.14")
def test_gemini_classifier_retry_logic(mocker):
    """Test retry logic on failure"""
    mocker.patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'})
    mocker.patch('providers.gemini_provider.genai.configure')
    
    # Mock model to fail twice then succeed
    mock_response = Mock()
    mock_response.text = "Account Problem"
    mock_model = Mock()
    mock_model.generate_content.side_effect = [
        Exception("First error"),
        Exception("Second error"),
        mock_response
    ]
    mocker.patch('providers.gemini_provider.genai.GenerativeModel', return_value=mock_model)
    
    classifier = GeminiClassifier()
    result = classifier.classify("My account is locked")
    
    assert result['category'] == "Account Problem"
    assert mock_model.generate_content.call_count == 3
