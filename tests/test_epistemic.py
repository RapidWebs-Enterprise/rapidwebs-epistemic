"""Tests for rapidwebs-epistemic plugin."""

from pathlib import Path
from unittest.mock import patch

import pytest

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from rapidwebs_epistemic import (
    ConfidenceEstimator,
    SelfModel,
)


class TestConfidenceEstimator:
    """Test confidence estimation logic."""

    def test_high_confidence_response(self):
        """Should assign high confidence to certain responses."""
        estimator = ConfidenceEstimator()

        result = estimator.estimate(
            user_message="How do I fix this bug?",
            assistant_response="The issue is a missing null check on line 42. "
            "Add: if response is None: return",
            transcript=[],
        )

        assert result["confidence"] >= 0.7
        assert not result["below_threshold"]

    def test_low_confidence_response(self):
        """Should flag uncertain responses."""
        estimator = ConfidenceEstimator()

        result = estimator.estimate(
            user_message="What's the best authentication method?",
            assistant_response="I'm not sure about the best approach. "
            "Maybe JWT? Or possibly OAuth2? "
            "It depends on your requirements.",
            transcript=[],
        )

        assert result["confidence"] < 0.7
        assert result["below_threshold"]

    def test_tool_verification_boost(self):
        """Should increase confidence with tool usage."""
        estimator = ConfidenceEstimator()

        transcript = [
            {"role": "assistant", "tool_calls": [{"id": "1", "name": "read_file"}]},
            {"role": "assistant", "tool_calls": [{"id": "2", "name": "search_files"}]},
        ]

        result = estimator.estimate(
            user_message="Find the auth module",
            assistant_response="Found it in src/auth.py",
            transcript=transcript,
        )

        # Tool usage should boost confidence
        assert result["factors"]["tool_verification"] > 0.3

    def test_uncertainty_markers(self):
        """Should detect uncertainty phrases."""
        estimator = ConfidenceEstimator()

        response = "I think it might be possible, but I'm not certain."
        count = estimator._count_uncertainty(response)

        assert count > 0  # Should detect uncertainty

    def test_certainty_markers(self):
        """Should recognize certainty phrases."""
        estimator = ConfidenceEstimator()

        response = "This is definitely the correct approach. Verified."
        count = estimator._count_uncertainty(response)

        assert count == 0  # No uncertainty detected

    def test_context_injection(self):
        """Should inject context for low-confidence responses."""
        estimator = ConfidenceEstimator(threshold=0.7)

        analysis = {
            "confidence": 0.45,
            "below_threshold": True,
            "recommendation": "verify before delivering",
        }

        injection = estimator.get_context_injection(analysis)

        assert injection is not None
        assert "CONFIDENCE: 0.45" in injection
        assert "verify" in injection.lower()

    def test_no_injection_for_high_confidence(self):
        """Should not inject context for high-confidence responses."""
        estimator = ConfidenceEstimator(threshold=0.7)

        analysis = {
            "confidence": 0.9,
            "below_threshold": False,
        }

        injection = estimator.get_context_injection(analysis)

        assert injection is None


class TestSelfModel:
    """Test self-model persistence and updates."""

    @pytest.fixture
    def model(self, tmp_path):
        """Create temporary self-model."""
        model_path = tmp_path / "self_model.json"
        with patch.object(SelfModel, "__init__", lambda self, path=model_path: None):
            model = SelfModel.__new__(SelfModel)
            model.path = model_path
            model.data = model._default_model()
            return model

    def test_load_nonexistent(self, tmp_path):
        """Should create default model when file doesn't exist."""
        model = SelfModel(path=tmp_path / "missing.json")

        assert model.data["capabilities"] == []
        assert model.data["past_mistakes"] == []

    def test_save_and_load(self, tmp_path):
        """Should persist and reload model."""
        model = SelfModel(path=tmp_path / "model.json")
        model.data["capabilities"] = ["debugging", "code_review"]
        model._save()

        # Reload
        model2 = SelfModel(path=tmp_path / "model.json")
        assert "debugging" in model2.data["capabilities"]

    def test_update_from_session(self, model):
        """Should extract lessons from session transcript."""
        transcript = [
            {
                "role": "assistant",
                "content": "Actually, I was wrong about that. "
                "The correct approach is...",
            }
        ]

        model.update_from_session("session_123", transcript)

        assert len(model.data["past_mistakes"]) > 0
        assert model.data["past_mistakes"][0]["type"] == "self_correction"

    def test_extract_preferences(self, model):
        """Should detect user preferences."""
        transcript = [
            {"role": "user", "content": "Be concise in your responses"},
            {"role": "user", "content": "Please provide step-by-step instructions"},
        ]

        model.update_from_session("session_456", transcript)

        assert model.data["preferences"]["style"] == "concise"
        assert model.data["preferences"]["format"] == "step-by-step"

    def test_get_context_injection(self, model):
        """Should inject self-model context."""
        model.data["past_mistakes"] = [
            {"type": "self_correction", "content": "Wrong about auth flow"},
        ]

        injection = model.get_context_injection()

        assert injection is not None
        assert "SELF-MODEL" in injection
        assert "auth flow" in injection.lower()

    def test_no_injection_when_empty(self, model):
        """Should return None when no mistakes."""
        model.data["past_mistakes"] = []

        injection = model.get_context_injection()

        assert injection is None


class TestPluginRegistration:
    """Test plugin registration."""

    def test_version(self):
        """Should have correct version."""
        import rapidwebs_epistemic

        assert rapidwebs_epistemic.version == "0.1.0"

    def test_description_exists(self):
        """Should have description."""
        import rapidwebs_epistemic

        assert hasattr(rapidwebs_epistemic, "description")
        assert len(rapidwebs_epistemic.description) > 0

    def test_tags_present(self):
        """Should have relevant tags."""
        import rapidwebs_epistemic

        assert "epistemic" in rapidwebs_epistemic.tags
        assert "confidence" in rapidwebs_epistemic.tags


class TestIntegration:
    """Integration tests for end-to-end workflows."""

    def test_full_confidence_workflow(self):
        """Test complete confidence estimation flow."""
        estimator = ConfidenceEstimator(threshold=0.7)

        # Low confidence response
        analysis = estimator.estimate(
            user_message="What's the capital of France?",
            assistant_response="I believe it might be Paris? Or possibly Lyon?",
            transcript=[],
        )

        assert analysis["below_threshold"]
        assert analysis["confidence"] < 0.7

        # High confidence response
        analysis = estimator.estimate(
            user_message="What's 2+2?",
            assistant_response="The answer is definitely 4.",
            transcript=[],
        )

        assert not analysis["below_threshold"]
        assert analysis["confidence"] >= 0.7
