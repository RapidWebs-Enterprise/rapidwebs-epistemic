---
name: epistemic-confidence-scoring
description: Agent confidence estimation system that scores responses 0.0-1.0 based on linguistic patterns, tool verification, and consistency analysis
status: proposed
created: 2026-09-20
author: Lucien (RapidWebs)
related-adrs: [ADR-001]
---

# Spec: Epistemic Confidence Scoring

## Context

Current Hermes agents deliver responses with uniform certainty regardless of actual confidence. Users cannot distinguish between well-verified answers and guesses. Research shows LLMs exhibit emergent metacognitive abilities (MUSE, 2025) but lack structured systems to leverage them.

**Problem:** No mechanism exists to quantify or communicate agent uncertainty.

**Solution:** Multi-factor confidence estimation with explicit threshold-based context injection.

## Requirements

### R1: Confidence Score Computation
The system SHALL compute a confidence score (0.0-1.0) for every agent response using weighted combination of:
- Linguistic certainty markers (25%)
- Tool verification density (30%)
- Response consistency with history (25%)
- Claim verifiability (20%)

#### Scenario: High-confidence response
- **GIVEN** agent responds with factual information verified by tool usage
- **WHEN** response contains certainty markers ("definitely", "confirmed") and multiple tool calls
- **THEN** confidence score >= 0.8 and no context injection occurs

#### Scenario: Low-confidence response
- **GIVEN** agent responds with uncertain language
- **WHEN** response contains uncertainty markers ("I'm not sure", "maybe") and no tools used
- **THEN** confidence score < 0.7 and context injection occurs with warning

### R2: Context Injection on Low Confidence
When confidence falls below threshold, the system SHALL inject context into user message containing:
- Confidence score (e.g., "[CONFIDENCE: 0.45]")
- Recommendation based on score level
- Suggested action (verify, escalate, skip)

#### Scenario: Moderate confidence
- **GIVEN** confidence score = 0.65
- **WHEN** pre_llm_call hook executes
- **THEN** context includes "[CONFIDENCE: 0.65] Moderate — consider verification"

### R3: Configuration
The system SHALL support configuration via plugin.yaml:
- `confidence_threshold`: Minimum confidence for direct delivery (default: 0.7)
- `enable_linguistic_analysis`: Toggle uncertainty marker detection
- `enable_tool_verification`: Toggle tool usage weighting
- `enable_history_consistency`: Toggle consistency checking

### R4: Performance
The system SHALL complete confidence estimation within 100ms to avoid user-visible latency.

## Non-Requirements

- Does NOT require access to model hidden states (black-box compatible)
- Does NOT modify base LLM behavior
- Does NOT persist confidence scores across sessions (stateless per-response)

## Design Notes

### Architecture
```
pre_llm_call hook
    ↓
ConfidenceEstimator.estimate()
    ↓
Factors computed:
  - linguistic_certainty_score (pattern matching)
  - tool_verification_score (tool call density)
  - consistency_score (history alignment)
  - verifiability_score (claim analysis)
    ↓
Weighted combination → confidence (0.0-1.0)
    ↓
If confidence < threshold:
  - Generate context injection
  - Return {"context": injection}
Else:
  - Return None (no injection)
```

### Data Model
```python
@dataclass
class ConfidenceAnalysis:
    confidence: float          # 0.0-1.0 overall score
    below_threshold: bool      # True if < threshold
    factors: dict              # Individual factor scores
    recommendation: str        # Actionable guidance
```

### Implementation Approach
1. Implement `ConfidenceEstimator` class in `__init__.py`
2. Register `pre_llm_call` hook in plugin.yaml
3. Extract uncertainty/certainty markers via regex
4. Count tool calls in recent transcript
5. Compute weighted score
6. Inject context when below threshold

## Open Questions

- How to handle multi-turn conversations with mixed confidence?
- Should confidence be tracked per-session for trend analysis?
- What threshold is optimal for different task types?

## References

- MUSE (Neural Networks 2025): Metacognition for Unknown Situations
- AutoMeco (EMNLP 2025): Meta-cognition Evaluation framework
- Evidence for Limited Metacognition in LLMs (arXiv:2509.21545)
- HTC: Holistic Trajectory Calibration (arXiv:2601.15778)
