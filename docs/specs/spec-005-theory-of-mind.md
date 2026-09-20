---
name: theory-of-mind-integration
description: User mental state modeling that infers goals, preferences, and emotional state from interaction history
status: proposed
created: 2026-09-20
author: Lucien (RapidWebs)
related-adrs: [ADR-005]
---

# Spec: Theory of Mind Integration

## Context

Current agents treat all users identically. They cannot infer user goals, adapt to preferences, or predict next requests. ToM-SWE (2025) shows 59.7% vs 18.1% task success with dedicated ToM agent.

**Problem:** No user mental state modeling.

**Solution:** Three-tier hierarchical user model updated per-session.

## Requirements

### R1: Three-Tier Memory Structure
The system SHALL maintain:
- **Tier 1:** Raw session storage (complete transcripts)
- **Tier 2:** Session-based user model (per-session analysis)
- **Tier 3:** Overall user model (cross-session patterns)

#### Scenario: New user
- **GIVEN** first interaction
- **WHEN** session ends
- **THEN** Tier 1 populated, Tier 2 created, Tier 3 initialized

#### Scenario: Returning user
- **GIVEN** user with existing models
- **WHEN** session ends
- **THEN** Tier 2 updated, Tier 3 aggregated

### R2: Mental State Inference
The system SHALL extract from each session:
- **Goals:** High-level objectives
- **Preferences:** Style, format, tool choices
- **Knowledge level:** Technical proficiency indicators
- **Emotional state:** Frustration, satisfaction markers

#### Scenario: Preference detection
- **GIVEN** user says "Be more concise"
- **WHEN** session analysis executes
- **THEN** preference.style = "concise" stored

#### Scenario: Frustration detection
- **GIVEN** user says "This is frustrating"
- **WHEN** session analysis executes
- **THEN** emotional_state = "frustrated" recorded

### R3: Prediction Engine
The system SHALL predict:
- Next likely request based on patterns
- Potential roadblocks based on history
- Appropriate communication style

#### Scenario: Pattern recognition
- **GIVEN** user always asks about database after auth
- **WHEN** auth completed
- **THEN** prediction: "user will ask about database"

### R4: Integration Points
- `on_session_end`: Update user models
- `pre_llm_call`: Inject user context
- Tool: `consult_tom()` for SWE agent queries

## Non-Requirements

- Does NOT replace Honcho peer representation
- Does NOT require real-time inference
- Does NOT store biometric data

## Design Notes

### Data Model
```python
@dataclass
class UserMentalState:
    goals: list[str]
    preferences: dict[str, str]
    knowledge_level: dict[str, str]
    emotional_state: Optional[str]
    interaction_history: list[dict]
```

### Update Frequency
- Tier 1: Every session (append)
- Tier 2: After each session (analyze)
- Tier 3: Daily aggregation (merge)

### Storage
- JSON files in `~/.hermes/epistemic/user_models/<user_id>/`
- Tier 1: `sessions/`
- Tier 2: `session_models/`
- Tier 3: `overall_model.json`

## Open Questions

- How to handle multiple users on same account?
- Should emotional states persist across sessions?
- How to validate prediction accuracy?

## References

- ToM-SWE (2025): Dual-agent architecture with ToM partner
- M3 (SOCIALIZE 2025): Mind modeling framework
- DPMT (2025): Dual process multi-scale Theory of Mind
- Inverse ToM (arXiv:2608.11354): Automated mental state inference
