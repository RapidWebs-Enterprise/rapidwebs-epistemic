"""Integration tests for rapidwebs-epistemic hooks."""

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from rapidwebs_epistemic import (
    ConfidenceEstimator,
    SelfModel,
    version,
)


class TestPluginRegistration:
    """Test plugin registration."""

    def test_version(self):
        """Should have correct version."""
        assert version == "0.1.0"

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


class TestConfidenceHookIntegration:
    """Test confidence estimation in hook-like context."""

    def test_pre_llm_call_injection(self):
        """Simulate pre_llm_call hook behavior."""
        estimator = ConfidenceEstimator(threshold=0.7)

        # Low confidence response
        analysis = estimator.estimate(
            user_message="What's the capital of France?",
            assistant_response="I think it might be Paris? Or possibly Lyon?",
            transcript=[],
        )

        # Should inject context
        context = estimator.get_context_injection(analysis)
        assert context is not None
        assert "CONFIDENCE:" in context
        assert "escalate" in context.lower() or "verify" in context.lower()

    def test_pre_llm_call_no_injection_high_confidence(self):
        """Should not inject for high confidence."""
        estimator = ConfidenceEstimator(threshold=0.7)

        analysis = estimator.estimate(
            user_message="What's 2+2?",
            assistant_response="The answer is definitely 4.",
            transcript=[],
        )

        context = estimator.get_context_injection(analysis)
        assert context is None


class TestSelfModelHookIntegration:
    """Test self-model in hook-like context."""

    def test_on_session_end_updates_model(self, tmp_path):
        """Simulate on_session_end hook."""
        model = SelfModel(path=tmp_path / "self_model.json")

        # Session with mistake
        transcript = [
            {
                "role": "assistant",
                "content": "Actually, I was wrong about that. "
                          "The correct approach is...",
            }
        ]

        model.update_from_session("test_session", transcript)

        # Verify persistence
        assert (tmp_path / "self_model.json").exists()
        data = json.loads((tmp_path / "self_model.json").read_text())
        assert len(data["past_mistakes"]) > 0

    def test_on_session_start_injects_context(self, tmp_path):
        """Simulate on_session_start hook."""
        model = SelfModel(path=tmp_path / "self_model.json")

        # Pre-populate with mistakes
        model.data["past_mistakes"] = [
            {
                "type": "self_correction",
                "content": "Wrong about auth flow",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ]
        model._save()

        # Reload and get injection
        model2 = SelfModel(path=tmp_path / "self_model.json")
        context = model2.get_context_injection()

        assert context is not None
        assert "SELF-MODEL" in context


class TestErrorHandling:
    """Test error recovery."""

    def test_malformed_json_recovery(self, tmp_path):
        """Should recover from corrupted JSON."""
        model_path = tmp_path / "self_model.json"
        model_path.write_text("{invalid json")

        model = SelfModel(path=model_path)

        # Should not crash, should use defaults
        assert model.data["capabilities"] == []
        assert model.data["past_mistakes"] == []

    def test_missing_directory_creation(self, tmp_path):
        """Should create parent directories."""
        nested_path = tmp_path / "nested" / "dir" / "model.json"

        model = SelfModel(path=nested_path)
        model.data["capabilities"] = ["test"]
        model._save()

        assert nested_path.exists()

        # Can reload
        model2 = SelfModel(path=nested_path)
        assert "test" in model2.data["capabilities"]


class TestPerformance:
    """Test performance requirements."""

    def test_confidence_estimation_latency(self):
        """Should complete in <100ms."""
        estimator = ConfidenceEstimator()

        start = time.perf_counter()
        for _ in range(100):
            estimator.estimate("test", "response", [])
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / 100) * 1000
        assert avg_ms < 100, f"Average latency {avg_ms:.2f}ms exceeds 100ms"

    def test_self_model_load_latency(self, tmp_path):
        """Load should be fast."""
        model_path = tmp_path / "model.json"
        model = SelfModel(path=model_path)
        model.data["capabilities"] = ["test"] * 100
        model._save()

        start = time.perf_counter()
        for _ in range(100):
            SelfModel(path=model_path)
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / 100) * 1000
        assert avg_ms < 10, f"Average load latency {avg_ms:.2f}ms"


class TestTTLPruning:
    """Test time-to-live pruning."""

    def test_prune_old_mistakes(self, tmp_path):
        """Should remove mistakes older than TTL."""
        from datetime import timezone as tz

        model = SelfModel(path=tmp_path / "model.json")

        # Add old mistake (manually backdate)
        old_timestamp = (datetime.now(tz.utc) - timedelta(days=100)).isoformat()
        model.data["past_mistakes"] = [
            {
                "type": "test",
                "content": "old mistake",
                "timestamp": old_timestamp,
            }
        ]
        model._save()

        # Reload and prune
        model2 = SelfModel(path=tmp_path / "model.json")
        model2._prune_old_mistakes()

        assert len(model2.data["past_mistakes"]) == 0

    def test_keep_recent_mistakes(self, tmp_path):
        """Should keep recent mistakes."""
        model = SelfModel(path=tmp_path / "model.json")

        # Add recent mistake
        recent_timestamp = datetime.now(timezone.utc).isoformat()
        model.data["past_mistakes"] = [
            {
                "type": "test",
                "content": "recent mistake",
                "timestamp": recent_timestamp,
            }
        ]
        model._save()

        # Prune
        model2 = SelfModel(path=tmp_path / "model.json")
        model2._prune_old_mistakes()

        assert len(model2.data["past_mistakes"]) == 1
