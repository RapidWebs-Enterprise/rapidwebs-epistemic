---
title: "ADR-005: Theory of Mind Data Model"
description: "Decision to use hierarchical three-tier model vs. flat structure"
category: architecture
tags:
  - epistemic
  - theory-of-mind
  - data-model
---

# ADR-005: Theory of Mind Data Model

**Status**: Accepted  
**Date**: 2026-09-20  
**Deciders**: Lucien (RapidWebs)  
**Consulted**: Steven Page  
**Informed**: Engineering team

## Context

We need to model user mental states for personalized interactions. Two data model approaches were considered:

**Option A: Flat Structure**
- Single JSON with all user data
- Simple queries
- Hard to scale

**Option B: Three-Tier Hierarchy**
- Tier 1: Raw sessions
- Tier 2: Session models
- Tier 3: Overall model
- Enables incremental refinement

## Decision

We will implement **Option B: Three-Tier Hierarchical Model**.

**Rationale:**
1. Matches ToM-SWE architecture (proven effective)
2. Enables incremental learning
3. Separates raw data from synthesized insights
4. Supports cross-session pattern detection

## Alternatives Considered

| Option | Description | Pros | Cons | Reason Rejected |
|--------|-------------|------|------|-----------------|
| **A** | Flat structure | Simple | No hierarchy | Cannot support incremental learning |
| **B** | Three-tier | Scalable | More complex | Chosen for proven effectiveness |

## Consequences

### Positive
- Proven architecture (ToM-SWE)
- Incremental refinement
- Clear separation of concerns
- Supports prediction engine

### Negative
- More storage locations
- Coordination between tiers
- Complex update logic

### Neutral/Follow-ups
- Could consolidate to flat if scale demands
- Could add tier 4 for group models

## Implementation Notes

- Directory: `~/.hermes/epistemic/user_models/<user_id>/`
- Tier 1: `sessions/` (JSONL transcripts)
- Tier 2: `session_models/` (per-session analysis)
- Tier 3: `overall_model.json` (aggregated)

## References

- ToM-SWE (2025): Three-tier hierarchical memory
- M3 (SOCIALIZE 2025): Mind modeling framework
- DPMT (2025): Multi-scale Theory of Mind
