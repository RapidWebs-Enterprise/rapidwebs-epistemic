"""Theory of Mind: User mental state modeling."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("rapidwebs-epistemic")


# ── Constants ────────────────────────────────────────────────────────────────

_TIER1_MAX_AGE_DAYS = 30
_TIER2_MAX_AGE_DAYS = 90
_TIER3_MAX_ENTRIES = 100

# Emotional state markers
FRUSTRATION_MARKERS = [
    "frustrated", "frustrating", "annoyed", "angry", "fed up", "tired of", "this is hard",
    "i give up", "this doesn't work", "wrong again"
]

SATISFACTION_MARKERS = [
    "thanks", "great", "perfect", "worked", "excellent", "love this",
    "finally", "got it", "success"
]

# Preference patterns
STYLE_PATTERNS = {
    "concise": ["be concise", "short", "brief", "to the point"],
    "thorough": ["be thorough", "detailed", "explain fully", "step by step"],
    "technical": ["technical", "detailed technical", "code first"],
    "simple": ["keep it simple", "plain English", "no jargon"],
}

FORMAT_PATTERNS = {
    "bullet_points": ["bullet points", "list format", "bullet list"],
    "tables": ["table format", "use a table"],
    "code_examples": ["show code", "example code", "code snippet"],
    "steps": ["step by step", "numbered steps", "stages"],
}


# ── Data Models ──────────────────────────────────────────────────────────────


@dataclass
class UserMentalState:
    """Complete user mental state model."""

    user_id: str
    goals: list[str] = field(default_factory=list)
    preferences: dict[str, str] = field(default_factory=dict)
    knowledge_level: dict[str, str] = field(default_factory=dict)
    emotional_history: list[dict] = field(default_factory=list)
    interaction_count: int = 0
    last_active: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "UserMentalState":
        """Deserialize from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class SessionModel:
    """Per-session extracted model."""

    session_id: str
    user_id: str
    extracted_preferences: dict[str, str] = field(default_factory=dict)
    extracted_goals: list[str] = field(default_factory=list)
    emotional_state: Optional[str] = None
    emotional_triggers: list[str] = field(default_factory=list)
    complexity_assessment: str = "medium"
    created_at: str = ""

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return asdict(self)


# ── Tier Implementations ─────────────────────────────────────────────────────


class Tier1Store:
    """Raw session transcript storage."""

    def __init__(self, base_path: Path, user_id: str = "default"):
        self.base_path = base_path
        self.user_id = user_id
        self.sessions_dir = base_path / "tier1" / "sessions" / user_id
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def store_session(self, session_id: str, user_id: str, transcript: list[dict]) -> None:
        """Store raw session transcript."""
        session_file = self.sessions_dir / f"{session_id}.jsonl"
        record = {
            "session_id": session_id,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "transcript": transcript,
        }
        with open(session_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def get_recent_sessions(self, user_id: str = None, days: int = 7) -> list[dict]:
        """Get recent sessions for analysis."""
        sessions = []
        cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)
        target_user = user_id or self.user_id

        for session_file in self.sessions_dir.glob("*.jsonl"):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    for line in f:
                        record = json.loads(line.strip())
                        record_ts = datetime.fromisoformat(record["timestamp"]).timestamp()
                        if record_ts >= cutoff and record.get("user_id") == target_user:
                            sessions.append(record)
            except (json.JSONDecodeError, OSError) as e:
                logger.debug("Failed to read session file %s: %s", session_file, e)

        return sorted(sessions, key=lambda x: x["timestamp"], reverse=True)

    def prune_old_sessions(self, max_age_days: int = _TIER1_MAX_AGE_DAYS) -> int:
        """Remove sessions older than max_age_days."""
        cutoff = datetime.now(timezone.utc).timestamp() - (max_age_days * 86400)
        pruned = 0

        for session_file in self.sessions_dir.glob("*.jsonl"):
            try:
                valid_lines = []
                with open(session_file, "r", encoding="utf-8") as f:
                    for line in f:
                        record = json.loads(line.strip())
                        record_ts = datetime.fromisoformat(record["timestamp"]).timestamp()
                        if record_ts >= cutoff:
                            valid_lines.append(line)

                if len(valid_lines) < len(list(open(session_file))):
                    with open(session_file, "w", encoding="utf-8") as f:
                        f.writelines(valid_lines)
                    pruned += 1
            except (json.JSONDecodeError, OSError):
                session_file.unlink(missing_ok=True)
                pruned += 1

        return pruned


class Tier2Store:
    """Per-session extracted models."""

    def __init__(self, base_path: Path, user_id: str = "default"):
        self.base_path = base_path
        self.user_id = user_id
        self.models_dir = base_path / "tier2" / "session_models" / user_id
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def save_model(self, model: SessionModel) -> None:
        """Save session model."""
        model_file = self.models_dir / f"{model.session_id}.json"
        with open(model_file, "w", encoding="utf-8") as f:
            json.dump(model.to_dict(), f, indent=2, ensure_ascii=False)

    def get_session_model(self, session_id: str) -> Optional[SessionModel]:
        """Get session model if exists."""
        model_file = self.models_dir / f"{session_id}.json"
        if model_file.exists():
            with open(model_file, "r", encoding="utf-8") as f:
                return SessionModel(**json.load(f))
        return None

    def get_recent_models(self, user_id: str = None, count: int = 10) -> list[SessionModel]:
        """Get recent session models."""
        target_user = user_id or self.user_id
        models = []
        for model_file in sorted(
            self.models_dir.glob("*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )[:count]:
            try:
                with open(model_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("user_id") == target_user:
                        models.append(SessionModel(**data))
            except (json.JSONDecodeError, OSError):
                continue
        return models


class Tier3Store:
    """Cross-session aggregated model."""

    def __init__(self, base_path: Path, user_id: str = "default"):
        self.base_path = base_path
        self.user_id = user_id
        self.model_file = base_path / "tier3" / "overall_model" / user_id / "model.json"
        self.model_file.parent.mkdir(parents=True, exist_ok=True)

    def load_model(self) -> UserMentalState:
        """Load or create overall model."""
        if self.model_file.exists():
            with open(self.model_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return UserMentalState.from_dict(data)
        return UserMentalState(
            user_id="",
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

    def save_model(self, model: UserMentalState) -> None:
        """Save overall model."""
        model.updated_at = datetime.now(timezone.utc).isoformat()
        with open(self.model_file, "w", encoding="utf-8") as f:
            json.dump(model.to_dict(), f, indent=2, ensure_ascii=False)

    def merge_session_model(self, session_model: SessionModel) -> UserMentalState:
        """Merge session model into overall model."""
        model = self.load_model()
        model.user_id = session_model.user_id

        # Merge preferences (newer wins)
        model.preferences.update(session_model.extracted_preferences)

        # Merge goals (deduplicate)
        for goal in session_model.extracted_goals:
            if goal not in model.goals:
                model.goals.append(goal)
                if len(model.goals) > _TIER3_MAX_ENTRIES:
                    model.goals.pop(0)

        # Track emotional patterns
        if session_model.emotional_state:
            model.emotional_history.append({
                "state": session_model.emotional_state,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "trigger": session_model.emotional_triggers[0] if session_model.emotional_triggers else None,
            })
            # Keep only last 50 emotional events
            model.emotional_history = model.emotional_history[-50:]

        model.interaction_count += 1
        model.last_active = datetime.now(timezone.utc).isoformat()

        self.save_model(model)
        return model


# ── Extraction Engine ────────────────────────────────────────────────────────


class ExtractionEngine:
    """Extract preferences, goals, and emotional state from transcripts."""

    def __init__(self):
        self.style_patterns = STYLE_PATTERNS
        self.format_patterns = FORMAT_PATTERNS

    def extract_from_transcript(self, transcript: list[dict]) -> SessionModel:
        """Extract mental state model from session transcript."""
        preferences = {}
        goals = []
        emotional_state = None
        emotional_triggers = []
        complexity = "medium"

        for msg in transcript:
            if not isinstance(msg, dict):
                continue

            content = msg.get("content", "")
            if not isinstance(content, str):
                continue

            content_lower = content.lower()

            # Extract preferences
            for style, patterns in self.style_patterns.items():
                if any(p in content_lower for p in patterns):
                    preferences["style"] = style
                    break

            for fmt, patterns in self.format_patterns.items():
                if any(p in content_lower for p in patterns):
                    preferences["format"] = fmt
                    break

            # Extract goals (from task completion)
            if any(phrase in content_lower for phrase in ["fix", "solve", "implement", "build", "create"]):
                goal = content[:100]
                if goal not in goals:
                    goals.append(goal)

            # Detect emotional state
            for marker in FRUSTRATION_MARKERS:
                if marker in content_lower:
                    emotional_state = "frustrated"
                    emotional_triggers.append(content[:50])
                    break

            if emotional_state != "frustrated":
                for marker in SATISFACTION_MARKERS:
                    if marker in content_lower:
                        emotional_state = "satisfied"
                        emotional_triggers.append(content[:50])
                        break

            # Assess complexity from assistant responses
            if msg.get("role") == "assistant":
                if len(content) > 1000:
                    complexity = "high"
                elif len(content) < 100:
                    complexity = "low"

        return SessionModel(
            session_id="",  # Set by caller
            user_id="",  # Set by caller
            extracted_preferences=preferences,
            extracted_goals=goals[:10],  # Max 10 goals
            emotional_state=emotional_state,
            emotional_triggers=emotional_triggers[-5:],  # Max 5 triggers
            complexity_assessment=complexity,
            created_at=datetime.now(timezone.utc).isoformat(),
        )


# ── Prediction Engine ────────────────────────────────────────────────────────


class PredictionEngine:
    """Predict next user requests based on patterns."""

    def __init__(self, tier3_store: Tier3Store):
        self.tier3 = tier3_store

    def predict_next_request(self) -> Optional[str]:
        """Predict likely next request."""
        model = self.tier3.load_model()

        if not model.goals:
            return None

        # Return most recent goal (simple heuristic)
        return f"Based on your previous work, you may want to continue with: {model.goals[-1]}"

    def predict_roadblocks(self) -> list[str]:
        """Predict potential roadblocks based on history."""
        model = self.tier3.load_model()
        roadblocks = []

        # Check for frustration patterns
        frustration_count = sum(
            1 for e in model.emotional_history
            if e.get("state") == "frustrated"
        )

        if frustration_count > 3:
            roadblocks.append("High frustration detected - consider simplifying approach")

        return roadblocks

    def get_context_injection(self) -> Optional[str]:
        """Generate context injection for agent."""
        model = self.tier3.load_model()
        if not model.preferences and not model.goals:
            return None

        lines = ["[USER MENTAL MODEL]"]

        if model.preferences:
            lines.append(f"Preferences: {model.preferences}")

        if model.goals:
            lines.append(f"Active goals: {', '.join(model.goals[-3:])}")

        if model.knowledge_level:
            lines.append(f"Knowledge areas: {model.knowledge_level}")

        return "\n".join(lines) + "\n"
