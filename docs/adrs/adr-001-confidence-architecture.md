---
title: "ADR-001: Confidence Estimation Architecture"
description: "Decision to use multi-factor heuristic confidence scoring vs. hidden state analysis"
category: architecture
tags:
  - epistemic
  - confidence
  - architecture
---

# ADR-001: Confidence Estimation Architecture

**Status**: Accepted  
**Date**: 2026-09-20  
**Deciders**: Lucien (RapidWebs)  
**Consulted**: Steven Page  
**Informed**: Engineering team

## Context

We need to estimate agent confidence to enable uncertainty-aware responses. Two architectural approaches were considered:

**Option A: Hidden State Analysis**
- Requires access to model internals (logits, attention weights)
- More accurate (FACTCHECKMATE achieves 70%+ detection)
- Only works with open models, not hosted APIs

**Option B: Heuristic Multi-Factor Scoring**
- Black-box compatible (works with any API)
- Lower accuracy but sufficient for practical use
- No model access required

## Decision

We will implement **Option B: Multi-Factor Heuristic Scoring**.

**Rationale:**
1. Hermes supports both open and closed models — solution must work with both
2. Research shows token probability variance correlates with correctness (r=0.5)
3. Heuristic approach is transparent and debuggable
4. Can be enhanced later with hidden state analysis for open models

## Alternatives Considered

| Option | Description | Pros | Cons | Reason Rejected |
|--------|-------------|------|------|-----------------|
| **A** | Hidden state analysis | Higher accuracy | Requires model access | Incompatible with hosted APIs |
| **B** | Verbalized confidence | Simple | Models lie about confidence | Unreliable per research |
| **C** | Multi-sample consistency | Robust | High latency (N× inference) | Too expensive for real-time |

## Consequences

### Positive
- Works with all LLM providers (OpenAI, Anthropic, Groq, local)
- Transparent and explainable
- Low latency (<100ms)
- Easy to debug and tune

### Negative
- Less accurate than hidden state methods
- Cannot detect sophisticated hallucinations
- Heuristic thresholds require tuning

### Neutral/Follow-ups
- May add hidden state support for open models in future
- Thresholds may need adjustment per task type
- Could incorporate CEB (Critic Experience Bank) pattern for self-improvement

## Implementation Notes

- ConfidenceEstimator class in `__init__.py`
- Hook integration via `pre_llm_call`
- Configurable thresholds in plugin.yaml

## References

- FACTCHECKMATE (EMNLP 2025): Hidden state detection
- MUSE (2025): Metacognition in LLMs
- AutoMeco (EMNLP 2025): Meta-cognition lenses
- CEB (2025): Critic Experience Bank
