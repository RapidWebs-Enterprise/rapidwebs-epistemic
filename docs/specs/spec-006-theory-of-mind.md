---
name: theory-of-mind-integration
description: Three-tier user mental state modeling with inference engine for personalized agent behavior
status: proposed
created: 2026-09-21
author: Lucien (RapidWebs)
related-adrs: [ADR-005]
---

# Spec: Theory of Mind Integration

## Context

Current epistemic plugin has confidence scoring and self-model persistence, but lacks **user mental state modeling**. Agents cannot infer user goals, preferences, or predict next requests based on interaction history.

**Problem:** No mechanism to model user psychology across sessions.

**Solution:** Three-tier hierarchical memory system with inference engine, based on ToM-SWE (2025) research showing 59.7% vs 18.1% task success with dedicated ToM agent.

## Requirements

### R1: Three-Tier Memory Structure
The system SHALL maintain:
- **Tier 1:** Raw session transcripts (append-only, time-bounded)
- **Tier 2:** Per-session user models (extracted preferences, goals, emotional state)
- **Tier 3:** Cross-session aggregated model (long-term patterns, consolidated preferences)

#### Scenario: New user first session
- **GIVEN** no prior user model exists
- **WHEN** session completes
- **THEN** Tier 1 stores transcript, Tier 2 creates empty model, Tier 3 initializes

#### Scenario: Returning user
- **GIVEN** user with existing Tier 2 and Tier 3 models
- **WHEN** session completes
- **THEN** Tier 2 updated, Tier 3 aggregated with new patterns

### R2: Mental State Inference
The system SHALL extract from each session:
- **Goals:** High-level objectives (inferred from tasks completed)
- **Preferences:** Style, format, tool choices (explicitly stated or inferred)
- **Knowledge level:** Technical proficiency indicators
- **Emotional state:** Frustration, satisfaction markers

#### Scenario: Preference detection
- **GIVEN** user says "Be more concise in your responses"
- **WHEN** session ends
- **THEN** `preferences.style = "concise"` stored in Tier 2

#### Scenario: Frustration detection
- **GIVEN** user says "This is frustrating" or "I'm tired of this"
- **WHEN** session ends
- **THEN** `emotional_state = "frustrated"` recorded with timestamp

### R3: Prediction Engine
The system SHALL predict:
- Next likely request based on conversation patterns
- Potential roadblocks based on historical difficulty
- Appropriate communication style for current context

#### Scenario: Pattern recognition
- **GIVEN** user always asks about database after auth
- **WHEN** auth completed
- **THEN** prediction: "user will ask about database" injected as context

### R4: Integration with Existing Components
The system SHALL integrate with:
- `ConfidenceEstimator` — adjust confidence based on user familiarity
- `SelfModel` — include user preferences in agent identity
- `EpistemicVigilance` — adjust verification strictness based on user expertise

## Non-Requirements

- Does NOT replace Honcho peer representation
- Does NOT require real-time inference (batch update per session)
- Does NOT store biometric or sensitive data
- Does NOT persist across different users on same account (per-user isolation)

## Design Notes

### Data Model
```python
@dataclass
class UserMentalState:
    user_id: str
    goals: list[str]
    preferences: dict[str, str]
    knowledge_level: dict[str, str]  # e.g., {"python": "expert", "devops": "intermediate"}
    emotional_history: list[dict]    # {"state": "frustrated", "timestamp": "...", "trigger": "..."}
    interaction_count: int
    last_active: datetime
```

### Tier Structure
```
~/.hermes/epistemic/users/<user_id>/
├── tier1/
│   └── sessions/
│       └── <session_id>.jsonl    # Raw transcripts
├── tier2/
│   └── session_models/
│       └── <session_id>.json     # Per-session analysis
└── tier3/
    └── overall_model.json        # Aggregated long-term model
```

### Update Frequency
- Tier 1: Every session (append)
- Tier 2: After each session (analyze)
- Tier 3: Daily aggregation (merge patterns)

## Open Questions

1. How to handle multiple users on same account?
2. Should emotional states persist across sessions?
3. How to validate prediction accuracy?
4. What's the optimal TTL for Tier 1 raw transcripts?

## References

- ToM-SWE (2025): Dual-agent architecture with ToM partner — 59.7% vs 18.1% success
- M3 (SOCIALIZE 2025): Mind modeling framework for personalization
- DPMT (2025): Dual process multi-scale Theory of Mind
- INWARD (NeurIPS 2025): Introspective access to own behavior
