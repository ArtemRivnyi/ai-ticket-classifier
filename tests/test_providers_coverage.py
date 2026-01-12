"""
Maximum coverage tests for providers
Target: 90%+ coverage for multi_provider.py and gemini_provider.py
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestMultiProviderCoverage:
    """Tests for providers/multi_provider.py coverage"""

    def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in CLOSED state"""
        from providers.multi_provider import CircuitBreaker, CircuitState

        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED

        # Successful call should keep it closed
        def success_func():
            return "success"

        result = cb.call(success_func)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert cb.failures == 0

    def test_circuit_breaker_opens_after_threshold(self):
        """Test circuit breaker opens after failure threshold"""
        from providers.multi_provider import CircuitBreaker, CircuitState

        cb = CircuitBreaker(failure_threshold=3, timeout=1)

        def fail_func():
            raise Exception("Test error")

        # First 2 failures should keep it closed
        for _ in range(2):
            try:
                cb.call(fail_func)
            except:
                pass
        assert cb.state == CircuitState.CLOSED

        # 3rd failure should open it
        try:
            cb.call(fail_func)
        except:
            pass
        assert cb.state == CircuitState.OPEN
        assert cb.failures == 3

    def test_circuit_breaker_open_state_raises(self):
        """Test circuit breaker in OPEN state raises exception"""
        from providers.multi_provider import CircuitBreaker, CircuitState
        from datetime import datetime, timedelta

        cb = CircuitBreaker(failure_threshold=1, timeout=100)
        cb.state = CircuitState.OPEN
        # Set last_failure_time to recent past so _should_attempt_reset returns False
        cb.last_failure_time = datetime.now() - timedelta(seconds=10)

        def func():
            return "success"

        with pytest.raises(Exception, match="Circuit breaker is open"):
            cb.call(func)

    def test_circuit_breaker_half_open_reset(self):
        """Test circuit breaker resets to HALF_OPEN after timeout"""
        from providers.multi_provider import CircuitBreaker, CircuitState
        from datetime import datetime, timedelta

        cb = CircuitBreaker(failure_threshold=1, timeout=1)
        cb.state = CircuitState.OPEN
        cb.last_failure_time = datetime.now() - timedelta(seconds=2)  # Past timeout

        def func():
            return "success"

        # Should transition to HALF_OPEN and allow call
        result = cb.call(func)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED

    def test_multi_provider_init_no_gemini(self, mocker):
        """Test MultiProvider initialization without Gemini"""
        # Remove GEMINI_API_KEY temporarily
        original_gemini_key = os.environ.pop("GEMINI_API_KEY", None)
        try:
            # The code checks for API key first, so without it gemini_available should be False
            # But we need to reload the module to get fresh initialization
            import importlib
            import providers.multi_provider

            importlib.reload(providers.multi_provider)
            from providers.multi_provider import MultiProvider

            provider = MultiProvider()
            # Without API key, gemini_available should be False
            assert provider.gemini_available is False
        finally:
            # Restore original key
            if original_gemini_key:
                os.environ["GEMINI_API_KEY"] = original_gemini_key
            # Reload module again to restore original state
            import importlib
            import providers.multi_provider

            importlib.reload(providers.multi_provider)

    def test_multi_provider_init_no_openai(self, mocker):
        """Test MultiProvider initialization without OpenAI"""
        # Remove OPENAI_API_KEY temporarily
        original_openai_key = os.environ.pop("OPENAI_API_KEY", None)
        try:
            # Without OPENAI_API_KEY, openai_available should be False
            # The code checks for API key first
            from providers.multi_provider import MultiProvider

            provider = MultiProvider()
            # Without API key, openai_available should be False
            assert provider.openai_available is False
        finally:
            # Restore original key
            if original_openai_key:
                os.environ["OPENAI_API_KEY"] = original_openai_key

    def test_multi_provider_classify_gemini_success(self):
        """Test successful Gemini classification"""
        from providers.multi_provider import MultiProvider

        provider = MultiProvider()
        provider.gemini_available = True
        provider.openai_available = False

        # Mock Gemini classifier classify method
        mock_gemini_classifier = Mock()
        mock_gemini_classifier.classify.return_value = {
            "category": "Network Issue",
            "confidence": 0.9,
            "provider": "gemini",
        }
        provider.gemini_classifier = mock_gemini_classifier

        result = provider.classify("VPN connection dropped")
        assert result["category"] == "Network Issue"
        assert result["provider"] == "gemini"

    def test_multi_provider_classify_gemini_fallback_to_openai(self, mocker):
        """Test MultiProvider.classify falls back to OpenAI when Gemini fails"""
        from providers.multi_provider import MultiProvider, CircuitState

        provider = MultiProvider()
        provider.gemini_available = True
        provider.openai_available = True

        # Mock gemini_classifier to raise exception
        mock_gemini_classifier = Mock()
        mock_gemini_classifier.classify.side_effect = Exception("Gemini error")
        provider.gemini_classifier = mock_gemini_classifier

        # Set circuit breaker to CLOSED so it tries Gemini first
        provider.gemini_circuit.state = CircuitState.CLOSED

        # Mock classify_with_openai method directly
        provider.classify_with_openai = Mock(
            return_value={
                "category": "Network Issue",
                "confidence": 0.8,
                "provider": "openai",
            }
        )

        result = provider.classify("test ticket")
        assert result["provider"] == "openai"
        assert "category" in result

    @pytest.mark.skipif(
        sys.version_info >= (3, 14),
        reason="Python 3.14 has compatibility issues with google-generativeai",
    )
    def test_gemini_provider_init_success(self, mocker):
        """Test GeminiClassifier initialization success"""
        # Skip if tenacity not available
        try:
            import tenacity
        except ImportError:
            pytest.skip("tenacity not installed")

        original_key = os.environ.get("GEMINI_API_KEY")
        try:
            os.environ["GEMINI_API_KEY"] = "test_key"
            # Patch google.generativeai before importing
            with patch("google.generativeai.configure") as mock_configure, patch(
                "google.generativeai.GenerativeModel"
            ) as mock_generative_model:
                mock_model = MagicMock()
                mock_generative_model.return_value = mock_model
                # Reload module to use mocked genai
                import importlib

                if "providers.gemini_provider" in sys.modules:
                    importlib.reload(sys.modules["providers.gemini_provider"])
                from providers.gemini_provider import GeminiClassifier

                provider = GeminiClassifier()
                assert provider.model is not None
                mock_configure.assert_called_once()
        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key
            elif "GEMINI_API_KEY" in os.environ:
                del os.environ["GEMINI_API_KEY"]

    @pytest.mark.skipif(
        sys.version_info >= (3, 14),
        reason="Python 3.14 has compatibility issues with google-generativeai",
    )
    def test_gemini_provider_init_no_key(self, mocker):
        """Test GeminiClassifier initialization without API key"""
        original_key = os.environ.pop("GEMINI_API_KEY", None)
        try:
            from providers.gemini_provider import GeminiClassifier

            with pytest.raises(ValueError, match="GEMINI_API_KEY not set"):
                provider = GeminiClassifier()
        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key

    @pytest.mark.skipif(
        sys.version_info >= (3, 14),
        reason="Python 3.14 has compatibility issues with google-generativeai",
    )
    def test_gemini_provider_classify_success(self, mocker):
        """Test GeminiClassifier.classify success"""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
            with patch("providers.gemini_provider.genai") as mock_genai:
                mock_model = MagicMock()
                mock_response = MagicMock()
                mock_response.text = "Network Issue"
                mock_model.generate_content.return_value = mock_response
                mock_genai.GenerativeModel.return_value = mock_model
                mock_genai.configure.return_value = None

                from providers.gemini_provider import GeminiClassifier

                provider = GeminiClassifier()
                result = provider.classify("test ticket")
                assert "category" in result
                assert result["provider"] == "gemini"

    @pytest.mark.skipif(
        sys.version_info >= (3, 14),
        reason="Python 3.14 has compatibility issues with google-generativeai",
    )
    def test_gemini_provider_classify_error(self, mocker):
        """Test GeminiClassifier.classify error handling"""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
            with patch("providers.gemini_provider.genai") as mock_genai:
                mock_model = MagicMock()
                mock_model.generate_content.side_effect = Exception("API error")
                mock_genai.GenerativeModel.return_value = mock_model
                mock_genai.configure.return_value = None

                from providers.gemini_provider import GeminiClassifier

                provider = GeminiClassifier()
                with pytest.raises(Exception):
                    provider.classify("test ticket")

    @pytest.mark.skipif(
        sys.version_info >= (3, 14),
        reason="Python 3.14 has compatibility issues with google-generativeai",
    )
    def test_gemini_provider_classify_not_available(self, mocker):
        """Test GeminiClassifier when API key not available"""
        original_key = os.environ.pop("GEMINI_API_KEY", None)
        try:
            from providers.gemini_provider import GeminiClassifier

            with pytest.raises(ValueError, match="GEMINI_API_KEY not set"):
                provider = GeminiClassifier()
        finally:
            if original_key:
                os.environ["GEMINI_API_KEY"] = original_key
