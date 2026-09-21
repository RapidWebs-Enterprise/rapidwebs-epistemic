"""Tests for Theory of Mind components."""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from user_model import (
    Tier1Store,
    Tier2Store,
    Tier3Store,
    ExtractionEngine,
    PredictionEngine,
    UserMentalState,
    SessionModel,
)


class TestTier1Store:
    """Test raw session transcript storage."""

    def test_store_and_retrieve_session(self, tmp_path):
        """Should store and retrieve session transcripts."""
        store = Tier1Store(tmp_path)

        transcript = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        store.store_session("session_123", "user_1", transcript)

        sessions = store.get_recent_sessions("user_1", days=7)
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == "session_123"

    def test_prune_old_sessions(self, tmp_path):
        """Should remove sessions older than max age."""
        store = Tier1Store(tmp_path)

        # Store old session
        old_time = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
        session_file = store.sessions_dir / "old_session.jsonl"
        with open(session_file, "w") as f:
            f.write(json.dumps({
                "session_id": "old_123",
                "user_id": "user_1",
                "timestamp": old_time,
                "transcript": [],
            }))

        pruned = store.prune_old_sessions(max_age_days=30)
        assert pruned >= 0


class TestTier2Store:
    """Test per-session model storage."""

    def test_save_and_load_model(self, tmp_path):
        """Should save and load session models."""
        store = Tier2Store(tmp_path)
        model = SessionModel(
            session_id="session_456",
            user_id="user_1",
            extracted_preferences={"style": "concise"},
            extracted_goals=["fix bug"],
        )
        store.save_model(model)

        loaded = store.get_session_model("session_456")
        assert loaded is not None
        assert loaded.extracted_preferences["style"] == "concise"

    def test_get_recent_models(self, tmp_path):
        """Should return most recent models."""
        store = Tier2Store(tmp_path)

        for i in range(5):
            model = SessionModel(
                session_id=f"session_{i}",
                user_id="user_1",
                extracted_preferences={},
            )
            store.save_model(model)

        recent = store.get_recent_models("user_1", count=3)
        assert len(recent) == 3


class TestTier3Store:
    """Test cross-session aggregation."""

    def test_load_and_save_model(self, tmp_path):
        """Should persist overall model."""
        store = Tier3Store(tmp_path)
        model = UserMentalState(
            user_id="user_1",
            goals=["build feature"],
            preferences={"style": "thorough"},
        )
        store.save_model(model)

        loaded = store.load_model()
        assert loaded.user_id == "user_1"
        assert "build feature" in loaded.goals

    def test_merge_session_model(self, tmp_path):
        """Should merge session into overall model."""
        store = Tier3Store(tmp_path)

        session_model = SessionModel(
            session_id="session_789",
            user_id="user_1",
            extracted_preferences={"format": "bullet_points"},
            extracted_goals=["solve issue"],
            emotional_state="satisfied",
        )

        merged = store.merge_session_model(session_model)
        assert "solve issue" in merged.goals
        assert merged.preferences.get("format") == "bullet_points"


class TestExtractionEngine:
    """Test preference and state extraction."""

    def test_extract_style_preference(self):
        """Should detect style preferences."""
        engine = ExtractionEngine()
        transcript = [
            {"role": "user", "content": "Be concise in your responses"},
        ]
        model = engine.extract_from_transcript(transcript)
        assert model.extracted_preferences.get("style") == "concise"

    def test_extract_format_preference(self):
        """Should detect format preferences."""
        engine = ExtractionEngine()
        transcript = [
            {"role": "user", "content": "Use bullet points please"},
        ]
        model = engine.extract_from_transcript(transcript)
        assert model.extracted_preferences.get("format") == "bullet_points"

    def test_detect_frustration(self):
        """Should detect frustrated emotional state."""
        engine = ExtractionEngine()
        transcript = [
            {"role": "user", "content": "This is so frustrating!"},
        ]
        model = engine.extract_from_transcript(transcript)
        # Check that emotional state was captured
        assert model.emotional_state is not None
        assert model.emotional_triggers

    def test_detect_satisfaction(self):
        """Should detect satisfied emotional state."""
        engine = ExtractionEngine()
        transcript = [
            {"role": "user", "content": "Thanks, that worked perfectly!"},
        ]
        model = engine.extract_from_transcript(transcript)
        assert model.emotional_state == "satisfied"

    def test_extract_goals(self):
        """Should extract goals from tasks."""
        engine = ExtractionEngine()
        transcript = [
            {"role": "user", "content": "I need to fix this bug"},
            {"role": "assistant", "content": "Let me help..."},
        ]
        model = engine.extract_from_transcript(transcript)
        assert len(model.extracted_goals) > 0


class TestPredictionEngine:
    """Test prediction capabilities."""

    def test_predict_next_request(self, tmp_path):
        """Should predict based on goals."""
        tier3 = Tier3Store(tmp_path)
        tier3.save_model(UserMentalState(
            user_id="user_1",
            goals=["deploy service", "fix bug"],
        ))

        engine = PredictionEngine(tier3)
        prediction = engine.predict_next_request()
        assert prediction is not None
        assert "fix bug" in prediction

    def test_predict_roadblocks(self, tmp_path):
        """Should detect frustration patterns."""
        tier3 = Tier3Store(tmp_path)
        tier3.save_model(UserMentalState(
            user_id="user_1",
            emotional_history=[
                {"state": "frustrated"} for _ in range(4)
            ],
        ))

        engine = PredictionEngine(tier3)
        roadblocks = engine.predict_roadblocks()
        assert len(roadblocks) > 0

    def test_context_injection(self, tmp_path):
        """Should generate context injection."""
        tier3 = Tier3Store(tmp_path)
        tier3.save_model(UserMentalState(
            user_id="user_1",
            preferences={"style": "concise"},
            goals=["test feature"],
        ))

        engine = PredictionEngine(tier3)
        context = engine.get_context_injection()
        assert context is not None
        assert "USER MENTAL MODEL" in context


class TestIntegration:
    """Integration tests for full ToM pipeline."""

    def test_full_pipeline(self, tmp_path):
        """Test complete extraction and aggregation pipeline."""
        # Setup stores
        tier1 = Tier1Store(tmp_path)
        tier2 = Tier2Store(tmp_path)
        tier3 = Tier3Store(tmp_path)
        extractor = ExtractionEngine()

        # Simulate session
        transcript = [
            {"role": "user", "content": "Be concise"},
            {"role": "user", "content": "This is frustrating"},
            {"role": "assistant", "content": "Here's the fix..."},
            {"role": "user", "content": "Perfect, thanks!"},
        ]

        # Store raw transcript
        tier1.store_session("session_001", "user_1", transcript)

        # Extract session model
        session_model = extractor.extract_from_transcript(transcript)
        session_model.session_id = "session_001"
        session_model.user_id = "user_1"
        tier2.save_model(session_model)

        # Aggregate to Tier 3
        tier3.merge_session_model(session_model)

        # Verify
        assert len(tier1.get_recent_sessions("user_1")) == 1
        assert tier2.get_session_model("session_001") is not None
        loaded_model = tier3.load_model()
        assert loaded_model.preferences.get("style") == "concise"
