---
title: "ADR-007: Confidence-Gated Retrieval for Conclusions"
description: "Decision to add multi-signal confidence scoring to KG queries for hallucination reduction"
category: architecture
tags:
  - honcho
  - retrieval
  - confidence
  - epistemic
version: 1.1
---

# ADR-007: Confidence-Gated Retrieval

**Status**: Proposed  
**Date**: 2026-09-21  
**Updated**: 2026-09-21  
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
- No schema changes required

### Negative
- Additional computation per query (~5ms)
- Config weight tuning required
- Provenance data increases response size
- May filter out legitimately relevant low-confidence info

### Neutral/Follow-ups
- Monitor query latency impact
- Tune weight defaults based on usage
- Consider caching high-confidence scores
- Add confidence distribution metrics

## Implementation Notes

1. **New module**: `src/utils/confidence.py` with `calculate_confidence()` function
2. **Schema extension**: Add `min_confidence` and `include_provenance` to `ConclusionQuery`
3. **Endpoint update**: Modify `/conclusions/query` to score and filter
4. **Response format**: Add `confidence`, `sources`, `contradictions` fields
5. **Integration**: Wire into epistemic vigilance plugin for claim verification

## Configuration

```yaml
# config.toml
[retrieval.confidence]
enabled = true
min_confidence_default = 0.3
weights = { source = 0.4, freshness = 0.3, consensus = 0.3 }
half_life_days = 7.0
```

## API Changes

### Request
```json
POST /v3/workspaces/{w}/conclusions/query
{
  "query": "What caused the failure?",
  "top_k": 20,
  "min_confidence": 0.5,
  "include_provenance": true
}
```

### Response
```json
{
  "conclusions": [
    {
      "id": "abc123",
      "text": "Database ran out of disk space",
      "confidence": 0.95,
      "sources": [
        {"type": "tool_result", "id": "disk_check", "timestamp": "..."}
      ],
      "contradictions": []
    }
  ],
  "retrieval_stats": {
    "total_matched": 47,
    "filtered_by_confidence": 27,
    "avg_confidence": 0.72
  }
}
```

## References

- Spec: spec-008-confidence-gated-retrieval.md (v1.1)
- SYNAPSE (ACL 2026): Triple hybrid retrieval with confidence
- Honcho epistemic plugin (existing confidence infrastructure)
- Mem0: Multi-signal retrieval fusion
