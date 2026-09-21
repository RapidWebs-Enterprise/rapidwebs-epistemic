---
title: "ADR-007: Confidence-Gated Retrieval for Conclusions"
description: "Decision to add multi-signal confidence scoring to KG queries for hallucination reduction"
category: architecture
tags:
  - honcho
  - retrieval
  - confidence
  - epistemic
---

# ADR-007: Confidence-Gated Retrieval

**Status**: Proposed  
**Date**: 2026-09-21  
**Deciders**: Lucien (RapidWebs)  
**Consulted**: Steven Page  
**Informed**: Engineering team

## Context

Honcho currently returns all matching conclusions without confidence scoring. Agents cannot distinguish "verified fact" from "maybe true" or "contradicted claim." This leads to hallucination-prone responses when agents cite low-confidence information.

**Current state:** Query endpoints return conclusions with semantic score only. No provenance or confidence metadata.

**Problem:** Agents lack signal to assess reliability of retrieved information.

## Decision

We will add multi-signal confidence scoring to conclusion retrieval:
- Source credibility (tool results > conversation > speculation)
- Temporal freshness (exponential decay)
- Consensus (number of independent sources)

Scores computed at query time (not persisted), with configurable minimum thresholds.

**Decision:** Extend `/conclusions/query` endpoint with `min_confidence` and `include_provenance` parameters.

## Alternatives Considered

| Option | Description | Pros | Cons | Reason Rejected |
|--------|-------------|------|------|-----------------|
| **A** | Score at query time (chosen) | No storage changes, always fresh | Computed on every query | Chosen for simplicity |
| **B** | Persist scores in DB | Faster queries | Stale scores, storage overhead | Rejected for complexity |
| **C** | LLM-based confidence | More accurate | Slow, expensive, inconsistent | Rejected for cost |

## Consequences

### Positive
- Reduces hallucination-prone responses
- Integrates with epistemic vigilance plugin
- Provides audit trail for agent decisions
- Backward compatible (optional parameters)

### Negative
- Additional computation per query (~5ms)
- Config weight tuning required
- Provenance data increases response size

### Neutral/Follow-ups
- Monitor query latency impact
- Tune weight defaults based on usage
- Consider caching high-confidence scores

## Implementation Notes

1. Add `calculate_confidence()` function in `src/utils/confidence.py`
2. Extend `ConclusionQuery` schema with `min_confidence` and `include_provenance`
3. Update `/conclusions/query` endpoint
4. Return provenance in response format
5. Wire into epistemic vigilance plugin

## References

- Spec: spec-008-confidence-gated-retrieval.md
- SYNAPSE (ACL 2026): Triple hybrid retrieval with confidence
- Honcho epistemic plugin (existing confidence infrastructure)
