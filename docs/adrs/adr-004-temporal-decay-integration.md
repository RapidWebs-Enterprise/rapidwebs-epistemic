---
title: "ADR-004: Temporal Decay Integration Point"
description: "Decision to wrap Honcho client vs. modifying Honcho core"
category: architecture
tags:
  - epistemic
  - temporal
  - integration
---

# ADR-004: Temporal Decay Integration Point

**Status**: Accepted  
**Date**: 2026-09-20  
**Deciders**: Lucien (RapidWebs)  
**Consulted**: Steven Page  
**Informed**: Engineering team

## Context

We need temporal decay for memory retrieval. Two integration approaches were considered:

**Option A: Modify Honcho Core**
- Direct implementation in Honcho
- Clean integration
- Requires maintaining fork

**Option B: Client Wrapper**
- Extend HonchoClient in plugin
- No core changes
- Plugin-managed

## Decision

We will implement **Option B: Client Wrapper**.

**Rationale:**
1. Honcho is maintained separately — avoid coupling
2. Plugin architecture allows independent updates
3. Can upgrade Honcho without re-implementing decay
4. Follows existing pattern (honcho_client.py)

## Alternatives Considered

| Option | Description | Pros | Cons | Reason Rejected |
|--------|-------------|------|------|-----------------|
| **A** | Modify Honcho core | Clean integration | Fork maintenance burden | Separation of concerns |
| **B** | Client wrapper | Independent updates | Slight abstraction overhead | Chosen for modularity |

## Consequences

### Positive
- Independent versioning
- Easy to upgrade Honcho
- Plugin responsibility
- No core modification risk

### Negative
- Abstraction layer overhead
- Must maintain wrapper compatibility
- Dual update paths

### Neutral/Follow-ups
- Could contribute decay feature upstream if adopted broadly
- Monitor Honcho for native decay support

## Implementation Notes

- `honcho_client.py` extends HonchoClient
- Decorator pattern for decay application
- Configurable half-life

## References

- Episodic Memory Position (arXiv:2502.06975): Temporal decay importance
- Honcho fork maintenance workflow
