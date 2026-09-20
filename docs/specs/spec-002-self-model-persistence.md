---
name: self-model-persistence
description: Persistent agent identity system that tracks capabilities, limitations, and past mistakes across sessions
status: proposed
created: 2026-09-20
author: Lucien (RapidWebs)
related-adrs: [ADR-002]
---

# Spec: Self-Model Persistence

## Context

Agents currently have no persistent identity or memory of past experiences. Each session starts from scratch, leading to repeated mistakes and inability to learn from experience. Research shows agents benefit from self-models (KnowSelf, ACL 2025; INWARD, NeurIPS 2025).

**Problem:** No mechanism for agents to maintain persistent identity across sessions.

**Solution:** JSON-based self-model with automatic extraction and session-end updates.

## Requirements

### R1: Self-Model Structure
The system SHALL maintain a JSON file at `~/.hermes/epistemic/self_model.json` with structure:
```json
{
  "version": "1.0.0",
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp",
  "capabilities": ["list", "of", "capabilities"],
  "limitations": ["list", "of", "limitations"],
  "past_mistakes": [
    {
      "type": "error_type",
      "content": "description",
      "timestamp": "ISO timestamp",
      "lesson": "what to do differently"
    }
  ],
  "preferences": {
    "style": "concise|thorough",
    "format": "step-by-step|overview"
  },
  "work_styles": {
    "best_practices": ["list"],
    "avoid_patterns": ["list"]
  }
}
```

### R2: Session-End Learning
On `on_session_end`, the system SHALL:
1. Analyze transcript for mistakes (self-corrections, uncertainty markers)
2. Extract user preferences from messages
3. Update self-model JSON file
4. Persist changes atomically

#### Scenario: Mistake detection
- **GIVEN** agent says "Actually, I was wrong about..." in transcript
- **WHEN** session ends
- **THEN** mistake is recorded in `past_mistakes` with type "self_correction"

#### Scenario: Preference extraction
- **GIVEN** user says "Be concise in your responses"
- **WHEN** session ends
- **THEN** `preferences.style` is set to "concise"

### R3: Session-Start Injection
On `on_session_start`, the system SHALL:
1. Load self-model from disk
2. Extract recent mistakes (last 3)
3. Inject as context into session

#### Scenario: First session
- **GIVEN** no self_model.json exists
- **WHEN** session starts
- **THEN** default empty model is created and no injection occurs

#### Scenario: Returning session
- **GIVEN** self_model.json contains past mistakes
- **WHEN** session starts
- **THEN** context includes "[SELF-MODEL — Recent Lessons]" with mistake summaries

### R4: Persistence and Recovery
The system SHALL:
- Use atomic write (temp file + rename) to prevent corruption
- Handle malformed JSON gracefully (recreate from defaults)
- Maintain backup of previous version

## Non-Requirements

- Does NOT require LLM fine-tuning
- Does NOT store sensitive user data
- Does NOT persist across different agents (agent-specific)

## Design Notes

### File Location
`~/.hermes/epistemic/self_model.json`

### Update Strategy
- Append-only for mistakes (max 50 entries, oldest pruned)
- Overwrite for preferences (full replacement)
- Timestamp on every update

### Mistake Classification
Types:
- `self_correction`: Agent explicitly corrects itself
- `user_correction`: User corrects agent
- `error_pattern`: Repeated error type detected
- `hallucination`: Factually incorrect statement identified

## Open Questions

- How to handle conflicting preferences from different users?
- Should mistakes expire after N days?
- How to distinguish one-off errors from patterns?

## References

- KnowSelf (ACL 2025): Agentic Knowledgeable Self-Awareness
- INWARD (NeurIPS 2025): Introspective Access to One's Own Behavior
- MAGELLAN (NeurIPS 2025): Metacognitive Generalization of Learning Progress
