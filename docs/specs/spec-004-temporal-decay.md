---
name: temporal-memory-decay
description: Time-based weighting for memory retrieval so recent context takes precedence over stale information
status: proposed
created: 2026-09-20
author: Lucien (RapidWebs)
related-adrs: [ADR-004]
---

# Spec: Temporal Memory Decay

## Context

Honcho stores all conclusions equally regardless of age. A 6-month-old fact competes with yesterday's context, causing relevance dilution. Human episodic memory naturally decays over time (Episodic Memory Position, 2025).

**Problem:** No temporal weighting in memory retrieval.

**Solution:** Exponential decay function applied to Honcho conclusion scores.

## Requirements

### R1: Decay Function
The system SHALL apply exponential temporal decay:
```
weight = exp(-age_days * ln(2) / half_life_days)
```
Default half-life: 7 days (50% weight reduction per week)

#### Scenario: Fresh conclusion
- **GIVEN** conclusion created 1 hour ago
- **WHEN** retrieval executes
- **THEN** weight ≈ 1.0 (no decay)

#### Scenario: Old conclusion
- **GIVEN** conclusion created 30 days ago
- **WHEN** retrieval executes
- **THEN** weight ≈ 0.004 (effectively zero)

### R2: Integration with Honcho
The system SHALL extend Honcho client to:
1. Fetch conclusions with timestamps
2. Apply temporal weighting
3. Sort by weighted relevance
4. Return top-K results

#### Scenario: Mixed-age retrieval
- **GIVEN** 10 conclusions: 5 fresh, 5 old
- **WHEN** query executes
- **THEN** fresh conclusions ranked higher

### R3: Configuration
The system SHALL support:
- `half_life_days`: Decay rate (default: 7)
- `min_weight`: Floor threshold (default: 0.01)
- `max_age_days`: Prune age (default: 365)

### R4: Pruning
The system SHALL periodically prune conclusions older than max_age_days during idle time.

## Non-Requirements

- Does NOT modify Honcho core code
- Does NOT affect existing API contracts
- Does NOT require Honcho restart

## Design Notes

### Implementation Approach
Wrapper around HonchoClient methods:
- `get_context_with_decay()` replaces `get_context()`
- `prune_old_conclusions()` runs on schedule

### Performance
- Decoding computed per-query (lightweight math)
- Pruning runs asynchronously
- No impact on write path

## Open Questions

- Should decay rate vary by entity type?
- Should user preferences override decay?
- How to handle critical long-term facts?

## References

- Episodic Memory Position (arXiv:2502.06975): Temporal decay essential
- SYNAPSE (ACL 2025): Temporal decay + lateral inhibition
- Nemori (2025): Adaptive memory distillation
