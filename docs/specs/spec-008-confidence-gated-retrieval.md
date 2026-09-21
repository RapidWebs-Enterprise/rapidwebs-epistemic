---
name: confidence-gated-retrieval
description: Score and filter KG conclusions by credibility, freshness, and consensus before returning to agents
status: proposed
created: 2026-09-21
author: Lucien (RapidWebs)
related-adrs: [ADR-007]
---

# Spec: Confidence-Gated Retrieval

## Context

Honcho currently returns all matching conclusions without confidence scoring. Agents cannot distinguish "verified fact" from "maybe true" or "contradicted claim." This leads to hallucination-prone responses when agents cite low-confidence information.

**Problem:** No confidence signal on retrieved conclusions.

**Solution:** Add credibility scoring based on source type, temporal freshness, and consensus, with configurable minimum thresholds.

## Requirements

### R1: Multi-Signal Confidence Scoring
The system SHALL compute confidence scores using three signals:
```
confidence = w1 * source_credibility + w2 * temporal_freshness + w3 * consensus
```

| Signal | Weight | Calculation |
|--------|--------|-------------|
| **Source Credibility** | 0.4 | Tool results: 1.0, conversation: 0.7, speculation: 0.3 |
| **Temporal Freshness** | 0.3 | Exponential decay from half-life config |
| **Consensus** | 0.3 | Number of independent sources confirming |

#### Scenario: High-confidence conclusion
- **GIVEN** conclusion from tool result, created 1 day ago, confirmed by 3 sources
- **WHEN** query executes
- **THEN** confidence ≈ 0.95

#### Scenario: Low-confidence conclusion
- **GIVEN** conclusion from speculation, created 60 days ago, no confirmation
- **WHEN** query executes
- **THEN** confidence ≈ 0.25

### R2: Minimum Confidence Threshold
The system SHALL support filtering by minimum confidence:
```python
# Query parameter
min_confidence: float = 0.3  # Default: include all
```

#### Scenario: Filter low-confidence results
- **GIVEN** 50 matching conclusions with mixed confidence
- **WHEN** query with `min_confidence=0.7`
- **THEN** only return conclusions with confidence ≥ 0.7

### R3: Provenance Tracking
Each conclusion SHALL include source traceability:
```json
{
  "text": "Honcho runs on port 8000",
  "confidence": 0.95,
  "sources": [
    {"type": "tool_result", "id": "podman_ps", "timestamp": "..."},
    {"type": "conversation", "id": "session_123", "timestamp": "..."}
  ],
  "contradictions": []
}
```

#### Scenario: Source verification
- **GIVEN** conclusion with multiple sources
- **WHEN** agent requests provenance
- **THEN** returns source list with timestamps and types

### R4: Integration with Epistemic Plugin
Confidence scores SHALL be consumed by the epistemic vigilance plugin:
- Low-confidence conclusions flagged as unverified
- High-confidence conclusions trusted by default
- Contradictions trigger vigilance warnings

## Non-Requirements

- Does NOT modify conclusion storage (scores computed at query time)
- Does NOT require LLM calls for scoring (heuristic-based)
- Does NOT persist confidence scores (computed on-demand)
- Does NOT affect existing API contracts (backward compatible)

## Design Notes

### Scoring Algorithm
```python
def calculate_confidence(conclusion: Conclusion) -> float:
    # Source credibility
    source_scores = {
        "tool_result": 1.0,
        "conversation": 0.7,
        "speculation": 0.3,
        "external_api": 0.9
    }
    source_score = source_scores.get(conclusion.source_type, 0.5)
    
    # Temporal freshness (exponential decay)
    age_days = (datetime.now() - conclusion.created_at).days
    freshness = math.exp(-age_days * ln(2) / HALF_LIFE_DAYS)
    
    # Consensus (logarithmic scaling)
    source_count = len(conclusion.sources)
    consensus = min(1.0, source_count / 5)  # Diminishing returns
    
    # Weighted combination
    confidence = (
        0.4 * source_score +
        0.3 * freshness +
        0.3 * consensus
    )
    
    return max(0.0, min(1.0, confidence))
```

### API Changes
```python
@router.post("/conclusions/query")
async def query_conclusions(
    query: str,
    top_k: int = 20,
    min_confidence: float = Query(0.0, ge=0.0, le=1.0),  # NEW
    include_provenance: bool = Query(True),  # NEW
    db: AsyncSession = read_db,
):
    """Query conclusions with confidence filtering."""
    results = await crud.query_conclusions(db, query, top_k)
    
    # Score and filter
    scored = []
    for c in results:
        c.confidence = calculate_confidence(c)
        if c.confidence >= min_confidence:
            scored.append(c)
    
    return scored
```

## Open Questions

1. Should source credibility weights be configurable per-workspace?
2. How to handle "unknown" source types?
3. Should we add confidence decay for stale contradictions?

## References

- SYNAPSE (ACL 2026): Triple hybrid retrieval with confidence gating
- Mem0: Multi-signal retrieval fusion
- Honcho temporal decay implementation
