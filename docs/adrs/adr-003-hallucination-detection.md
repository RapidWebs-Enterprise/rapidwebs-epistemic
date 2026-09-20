---
title: "ADR-003: Hallucination Detection Approach"
description: "Decision to use lightweight post-hoc verification vs. preemptive hidden state analysis"
category: architecture
tags:
  - epistemic
  - hallucination
  - verification
---

# ADR-003: Hallucination Detection Approach

**Status**: Accepted  
**Date**: 2026-09-20  
**Deciders**: Lucien (RapidWebs)  
**Consulted**: Steven Page  
**Informed**: Engineering team

## Context

Hallucinations are a critical reliability concern. We need to detect and flag them. Two approaches were considered:

**Option A: Preemptive Detection (FACTCHECKMATE)**
- Analyzes hidden states before generation
- 70%+ detection accuracy
- Requires model access

**Option B: Post-hoc Verification (HalMit-inspired)**
- Checks claims against available sources after generation
- Black-box compatible
- Lower accuracy but practical

## Decision

We will implement **Option B: Post-hoc Verification** for v1, with architecture allowing Option A for future.

**Rationale:**
1. Must work with all LLM providers (open + closed)
2. Can leverage existing Honcho KG for verification
3. Non-blocking (runs async after response)
4. Can be enhanced later with hidden state access

## Alternatives Considered

| Option | Description | Pros | Cons | Reason Rejected |
|--------|-------------|------|------|-----------------|
| **A** | Preemptive detection | Higher accuracy | Requires model access | Incompatible with APIs |
| **B** | Post-hoc verification | Black-box compatible | Lower accuracy | Chosen for compatibility |
| **C** | Multi-agent debate | Robust | High latency/cost | Too expensive for v1 |

## Consequences

### Positive
- Works with any LLM provider
- Leverages existing Honcho KG
- Non-blocking (async)
- Extensible architecture

### Negative
- Cannot prevent hallucinations (only flag after)
- May miss subtle hallucinations
- Requires source data to verify against

### Neutral/Follow-ups
- Add hidden state support for open models
- Integrate with CEB pattern for self-improvement
- Consider GUARDIAN-style graph modeling for multi-agent

## Implementation Notes

- EpistemicVigilance class in `__init__.py`
- Hook: `post_llm_call`
- Sources: Honcho KG, tool results, session context
- Async execution to avoid latency

## References

- HalMit (arXiv:2507.15903): Black-box watchdog
- FACTCHECKMATE (EMNLP 2025): Preemptive detection
- HADEMIF (ICLR 2025): Dual-space detection
- InEx (AAAI 2025): Multi-agent verification
