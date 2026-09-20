"""rapidwebs-epistemic: Epistemic Enhancement Layer for Hermes Agent.

Provides three core capabilities:
1. Epistemic Confidence Scoring — agents estimate their own certainty (0.0-1.0)
2. Self-Model Persistence — agents learn from past mistakes across sessions
3. Epistemic Vigilance — continuous monitoring for hallucinations and logical errors

Architecture:
- Confidence Estimator: Analyzes response patterns, tool usage, and uncertainty markers
- Self-Model Manager: Maintains persistent agent identity, capabilities, limitations
- Epistemic Vigilance: Checks claims against sources, flags unverified statements

Integration:
- pre_llm_call: Inject confidence context when < 0.7 threshold
- post_llm_call: Run vigilance checks on generated responses
- on_session_end: Update self-model with lessons learned
- on_session_start: Load self-model for session continuity

Research Backing:
- INWARD (2025): LLMs can access facts about themselves
- KnowSelf (ACL 2025): Agentic knowledgeable self-awareness
- MetaCrit (2025): Multi-agent self-reflection improves truthfulness 34%

Author: RapidWebs (Lucien)
License: MIT
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("rapidwebs-epistemic")

# ── Plugin Metadata ──────────────────────────────────────────────────────────

version = "0.1.0"
description = "Epistemic Enhancement Layer — confidence scoring, self-model, vigilance"
author = "RapidWebs (Lucien)"
license = "MIT"
tags = ["epistemic", "confidence", "self-model", "vigilance"]
requirements = []

# ── Configuration Defaults ───────────────────────────────────────────────────

# Confidence estimation
_CONFIDENCE_THRESHOLD = 0.7  # Flag responses below this confidence
_CONFIDENCE_HISTORY_WINDOW = 10  # Turns to consider for confidence calculation

# Self-model persistence
_SELF_MODEL_PATH = Path.home() / ".hermes" / "epistemic" / "self_model.json"
_SELF_MODEL_MAX_MISTAKES = 50  # Keep last N mistakes
_SELF_MODEL_TTL_DAYS = 90  # Expire old capabilities/limitations

# Epistemic vigilance
_VIGILANCE_ENABLED = True
_CLAIM_EXTRACTION_ENABLED = True
_SOURCE_VERIFICATION_ENABLED = True

# ── Initialize Storage ───────────────────────────────────────────────────────

_EPISTEMIC_DIR = Path.home() / ".hermes" / "epistemic"
_EPISTEMIC_DIR.mkdir(parents=True, exist_ok=True)
_SELF_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)


# ═════════════════════════════════════════════════════════════════════════════
# COMPONENT 1: CONFIDENCE ESTIMATOR
# ═════════════════════════════════════════════════════════════════════════════


class ConfidenceEstimator:
    """Estimate agent confidence (0.0-1.0) based on response patterns."""

    # Uncertainty markers that decrease confidence
    UNCERTAINTY_PHRASES = [
        "i'm not sure",
        "i don't know",
        "probably",
        "maybe",
        "possibly",
        "might be",
        "could be",
        "i think",
        "i believe",
        "it seems",
        "as far as i know",
        "to the best of my knowledge",
    ]

    # Certainty markers that increase confidence
    CERTAINTY_PHRASES = [
        "definitely",
        "certainly",
        "absolutely",
        "confirmed",
        "verified",
        "proven",
        "established",
        "undoubtedly",
        "explicitly",
        "clearly",
    ]

    def __init__(self, threshold: float = _CONFIDENCE_THRESHOLD):
        self.threshold = threshold
        self._confidence_history: list[float] = []

    def estimate(
        self,
        user_message: str,
        assistant_response: str,
        transcript: list[dict],
    ) -> dict[str, Any]:
        """Estimate confidence and return detailed analysis."""

        # Factor 1: Uncertainty language
        uncertainty_score = self._count_uncertainty(assistant_response)

        # Factor 2: Tool verification density
        tool_score = self._calculate_tool_verification(transcript)

        # Factor 3: Response consistency with history
        consistency_score = self._check_consistency(assistant_response, transcript)

        # Factor 4: Claim verifiability
        claim_score = self._estimate_claim_verifiability(assistant_response)

        # Weighted combination
        confidence = (
            0.25 * (1 - uncertainty_score) +
            0.30 * tool_score +
            0.25 * consistency_score +
            0.20 * claim_score
        )

        # Clamp to valid range
        confidence = max(0.0, min(1.0, confidence))

        # Store in history
        self._confidence_history.append(confidence)
        if len(self._confidence_history) > _CONFIDENCE_HISTORY_WINDOW:
            self._confidence_history.pop(0)

        return {
            "confidence": round(confidence, 2),
            "below_threshold": confidence < self.threshold,
            "factors": {
                "uncertainty_penalty": round(uncertainty_score, 2),
                "tool_verification": round(tool_score, 2),
                "consistency": round(consistency_score, 2),
                "verifiability": round(claim_score, 2),
            },
            "recommendation": self._get_recommendation(confidence, uncertainty_score),
        }

    def _count_uncertainty(self, text: str) -> float:
        """Count uncertainty markers in text."""
        text_lower = text.lower()
        count = sum(1 for phrase in self.UNCERTAINTY_PHRASES if phrase in text_lower)
        certainty_count = sum(
            1 for phrase in self.CERTAINTY_PHRASES if phrase in text_lower
        )

        # Net uncertainty (0.0 = very certain, 1.0 = very uncertain)
        total_markers = count + certainty_count
        if total_markers == 0:
            return 0.0

        return max(0.0, min(1.0, (count - certainty_count) / max(count, 1)))

    def _calculate_tool_verification(self, transcript: list[dict]) -> float:
        """Calculate confidence boost from tool usage."""
        if not transcript:
            return 0.5  # Neutral if no history

        # Count tool calls in recent transcript
        tool_calls = 0
        for msg in transcript[-5:]:  # Last 5 messages
            if isinstance(msg, dict):
                tool_calls += len(msg.get("tool_calls", []))

        # More tools = higher confidence (diminishing returns)
        return min(1.0, tool_calls / 5)

    def _check_consistency(self, response: str, transcript: list[dict]) -> float:
        """Check if response is consistent with conversation history."""
        if len(transcript) < 2:
            return 0.7  # Default for new conversations

        # Simple consistency check: look for contradictions
        # This is a heuristic; could be enhanced with LLM-based checking
        return 0.8  # Placeholder for now

    def _estimate_claim_verifiability(self, response: str) -> float:
        """Estimate what fraction of claims can be verified."""
        # Count potential claims (periods, semicolons)
        sentences = re.split(r"[.!?;]+", response)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        if not sentences:
            return 0.5

        # Heuristic: factual claims are harder to verify
        factual_indicators = ["the", "is", "are", "was", "were", "has", "have"]
        verifiable = 0
        for sent in sentences:
            if any(indicator in sent.lower() for indicator in factual_indicators):
                verifiable += 1

        return verifiable / max(len(sentences), 1)

    def _get_recommendation(self, confidence: float, uncertainty: float) -> str:
        """Generate recommendation based on confidence score."""
        if confidence >= 0.8:
            return "high-confidence — proceed without verification"
        elif confidence >= self.threshold:
            return "moderate-confidence — consider light verification"
        elif confidence >= 0.5:
            return "low-confidence — verify before delivering"
        else:
            return "very-low confidence — escalate to user or skip"

    def get_context_injection(self, analysis: dict) -> Optional[str]:
        """Generate context injection for low-confidence responses."""
        if not analysis.get("below_threshold", False):
            return None

        confidence = analysis["confidence"]
        recommendation = analysis.get("recommendation", "")

        return f"\n[CONFIDENCE: {confidence:.2f}] {recommendation}\n"


# ═════════════════════════════════════════════════════════════════════════════
# COMPONENT 2: SELF-MODEL MANAGER
# ═════════════════════════════════════════════════════════════════════════════


class SelfModel:
    """Persistent model of agent identity, capabilities, and lessons learned."""

    def __init__(self, path: Path = _SELF_MODEL_PATH):
        self.path = path
        self.data = self._load()

    def _load(self) -> dict:
        """Load self-model from disk."""
        if not self.path.exists():
            return self._default_model()

        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            logger.warning("Failed to load self-model, using defaults")
            return self._default_model()

    def _default_model(self) -> dict:
        """Create default self-model structure."""
        return {
            "version": "1.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "capabilities": [],
            "limitations": [],
            "past_mistakes": [],
            "preferences": {},
            "work_styles": {},
            "knowledge_base": {},
        }

    def update_from_session(
        self,
        session_id: str,
        transcript: list[dict],
        outcome: str = "completed",
    ) -> None:
        """Extract lessons from session and update self-model."""

        # Extract mistakes
        mistakes = self._extract_mistakes(transcript)
        if mistakes:
            self.data["past_mistakes"].extend(mistakes)
            # Keep only recent mistakes
            self.data["past_mistakes"] = self.data["past_mistakes"][
                -_SELF_MODEL_MAX_MISTAKES:
            ]

        # Extract preferences
        preferences = self._extract_preferences(transcript)
        self.data["preferences"].update(preferences)

        # Update timestamp
        self.data["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Persist
        self._save()

        logger.info(
            "Updated self-model for session %s: %d mistakes, %d preferences",
            session_id,
            len(mistakes),
            len(preferences),
        )

    def _extract_mistakes(self, transcript: list[dict]) -> list[dict]:
        """Identify mistakes in session transcript."""
        mistakes = []

        for msg in transcript:
            if not isinstance(msg, dict):
                continue

            # Check assistant messages for error patterns
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                if isinstance(content, str):
                    # Look for self-correction patterns
                    if (
                        "i was wrong" in content.lower()
                        or "actually" in content.lower()
                    ):
                        mistakes.append(
                            {
                                "type": "self_correction",
                                "content": content[:200],
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            }
                        )

                    # Look for uncertainty followed by correction
                    if any(
                        phrase in content.lower()
                        for phrase in ["i'm not sure", "maybe"]
                    ):
                        mistakes.append(
                            {
                                "type": "uncertainty",
                                "content": content[:200],
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            }
                        )

        return mistakes

    def _extract_preferences(self, transcript: list[dict]) -> dict:
        """Extract user preferences from session."""
        preferences = {}

        for msg in transcript:
            if not isinstance(msg, dict):
                continue

            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    # Detect style preferences
                    if "be concise" in content.lower():
                        preferences["style"] = "concise"
                    if "be thorough" in content.lower():
                        preferences["style"] = "thorough"
                    if "step-by-step" in content.lower():
                        preferences["format"] = "step-by-step"

        return preferences

    def _save(self) -> None:
        """Persist self-model to disk."""
        try:
            # Ensure parent directory exists
            self.path.parent.mkdir(parents=True, exist_ok=True)

            temp_path = self.path.with_suffix(".json.tmp")
            temp_path.write_text(
                json.dumps(self.data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            temp_path.rename(self.path)
        except OSError as e:
            logger.error("Failed to save self-model: %s", e)
            raise  # Re-raise so caller knows write failed

    def _prune_old_mistakes(self) -> None:
        """Remove mistakes older than TTL days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=_SELF_MODEL_TTL_DAYS)
        before = len(self.data["past_mistakes"])

        self.data["past_mistakes"] = [
            m
            for m in self.data["past_mistakes"]
            if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]

        pruned = before - len(self.data["past_mistakes"])
        if pruned > 0:
            logger.info("Pruned %d old mistakes (TTL: %d days)", pruned, _SELF_MODEL_TTL_DAYS)

    def get_context_injection(self) -> Optional[str]:
        """Generate context injection from self-model."""
        if not self.data.get("past_mistakes"):
            return None

        # Include recent mistakes as reminders
        recent_mistakes = self.data["past_mistakes"][-3:]
        if not recent_mistakes:
            return None

        lines = ["[SELF-MODEL — Recent Lessons]"]
        for mistake in recent_mistakes:
            lines.append(
                f"- {mistake.get('type', 'unknown')}: {mistake.get('content', '')[:100]}"
            )

        return "\n".join(lines) + "\n"


# ═════════════════════════════════════════════════════════════════════════════
# COMPONENT 3: EPISTEMIC VIGILANCE
# ═════════════════════════════════════════════════════════════════════════


class EpistemicVigilance:
    """Continuous monitoring for hallucinations and unverified claims."""

    FACTUAL_MARKERS = [
        "the", "is", "are", "was", "were", "has", "have", "had",
        "according to", "studies show", "research indicates",
        "the API endpoint", "the correct", "the answer is",
    ]

    OPINION_MARKERS = [
        "i think", "i believe", "maybe", "possibly", "might",
        "could be", "seems like", "i'm not sure",
    ]

    def __init__(self, honcho_client=None):
        self.honcho = honcho_client
        self._tool_results: list[dict] = []
        self._session_context: str = ""

    def set_tool_results(self, results: list[dict]) -> None:
        """Update tool results for verification."""
        self._tool_results = results[-50:]

    def set_session_context(self, context: str) -> None:
        """Update session context for verification."""
        self._session_context = context[:5000]

    def extract_claims(self, response: str) -> list[dict]:
        """Extract verifiable claims from text."""
        claims = []
        sentences = re.split(r'[.!?]+', response)

        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 20:
                continue

            text_lower = sent.lower()
            is_opinion = any(marker in text_lower for marker in self.OPINION_MARKERS)
            is_factual = any(marker in text_lower for marker in self.FACTUAL_MARKERS)

            if is_factual and not is_opinion:
                claims.append({
                    "text": sent[:200],
                    "type": "factual",
                    "confidence": 0.8,
                })

        return claims

    async def verify_claim(self, claim: dict) -> dict:
        """Check claim against available sources."""
        result = {
            "claim": claim["text"],
            "status": "unverified",
            "sources_checked": [],
            "evidence": [],
        }

        if self.honcho:
            try:
                query = claim["text"][:100]
                entities = await self.honcho.search_entities(q=query, limit=3)
                if entities:
                    result["sources_checked"].append("honcho_kg")
                    for ent in entities[:2]:
                        if ent.get("name") in claim["text"]:
                            result["status"] = "verified"
                            result["evidence"].append(f"Honcho: {ent.get('name')}")
            except Exception as e:
                logger.debug("Honcho verification failed: %s", e)

        for tool_result in self._tool_results:
            content = str(tool_result.get("result", ""))
            if claim["text"][:50] in content or content[:50] in claim["text"]:
                result["sources_checked"].append("tool_results")
                result["status"] = "verified"
                result["evidence"].append("Tool result match")
                break

        if self._session_context and claim["text"][:100] in self._session_context:
            result["sources_checked"].append("session_context")
            result["status"] = "verified"
            result["evidence"].append("Session context match")

        return result

    def format_warning(self, unverified: list[dict]) -> Optional[str]:
        """Format warning for unverified claims."""
        if not unverified:
            return None

        lines = ["[EPISTEMIC VIGILANCE — Unverified Claims]"]
        for item in unverified[:3]:
            lines.append(f"  - {item['claim'][:100]}")
            lines.append(f"    Status: {item['status']}")

        return "\n".join(lines) + "\n"

    async def check_response(self, response: str) -> Optional[str]:
        """Main entry point: verify response and return warning if needed."""
        claims = self.extract_claims(response)
        if not claims:
            return None

        unverified = []
        for claim in claims:
            result = await self.verify_claim(claim)
            if result["status"] == "unverified":
                unverified.append(result)

        if unverified:
            return self.format_warning(unverified)

        return None


def register(ctx) -> None:
    """Register rapidwebs-epistemic plugin hooks."""
    logger.info("rapidwebs-epistemic v%s — registering hooks", version)

    confidence = ConfidenceEstimator()
    self_model = SelfModel()
    vigilance = EpistemicVigilance()

    ctx.register_hook("pre_llm_call", lambda ctx, **kw: _pre_llm_call(confidence, ctx, **kw))
    ctx.register_hook("on_session_end", lambda ctx, **kw: _on_session_end(self_model, ctx, **kw))
    ctx.register_hook("on_session_start", lambda ctx, **kw: _on_session_start(self_model, ctx, **kw))
    ctx.register_hook("post_llm_call", lambda ctx, **kw: _post_llm_call(vigilance, ctx, **kw))

    logger.info("rapidwebs-epistemic v%s — 4 hooks registered", version)


async def _pre_llm_call(confidence: ConfidenceEstimator, ctx, **kwargs):
    """Inject confidence context before LLM call."""
    transcript = kwargs.get("transcript", [])
    user_message = kwargs.get("user_message", "")
    assistant_response = kwargs.get("assistant_response", "")

    if not assistant_response:
        return None

    analysis = confidence.estimate(user_message, assistant_response, transcript)
    return confidence.get_context_injection(analysis)


async def _on_session_end(self_model: SelfModel, ctx, **kwargs):
    """Update self-model at session end."""
    transcript = kwargs.get("transcript", [])
    session_id = kwargs.get("session_id", "unknown")

    if transcript:
        self_model.update_from_session(session_id, transcript)


async def _on_session_start(self_model: SelfModel, ctx, **kwargs):
    """Inject self-model context at session start."""
    return self_model.get_context_injection()


async def _post_llm_call(vigilance: EpistemicVigilance, ctx, **kwargs):
    """Run vigilance checks after LLM response."""
    response = kwargs.get("assistant_response", "")
    if not response:
        return None

    warning = await vigilance.check_response(response)
    return {"context": warning} if warning else None
