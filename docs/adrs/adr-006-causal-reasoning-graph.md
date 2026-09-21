---
title: "ADR-006: Causal Reasoning Graph for Honcho KG"
description: "Decision to add causal edge types with bidirectional inference for troubleshooting and 'why' queries"
category: architecture
tags:
  - honcho
  - knowledge-graph
  - causal-reasoning
---

# ADR-006: Causal Reasoning Graph

**Status**: Proposed  
**Date**: 2026-09-21  
**Deciders**: Lucien (RapidWebs)  
**Consulted**: Steven Page  
**Informed**: Engineering team

## Context

Honcho's Knowledge Graph currently captures entities and relationships but lacks explicit causal modeling. When an agent asks "Why did the deployment fail?", the system cannot traverse cause-effect chains—it only knows "what" is connected, not "why."

**Current state:** KG supports semantic, temporal, and entity relationships. No causal edges.

**Problem:** Agents cannot perform root-cause analysis or predict cascading effects.

## Decision

We will add a `KGCausalRelationship` edge type with:
- Bidirectional traversal (cause→effect and effect←cause)
- Confidence scoring per causal link
- Evidence text for audit trails
- Temporal validity windows

**Decision:** Implement causal edges as a new relationship type in the KG schema, with dedicated query endpoints for "why" and "what happened" traversal.

## Alternatives Considered

| Option | Description | Pros | Cons | Reason Rejected |
|--------|-------------|------|------|-----------------|
| **A** | Add causal edges to existing KG | Simple, consistent | Mixed edge types complicate queries | Chosen for simplicity |
| **B** | Separate causal graph | Clean separation | Duplication, sync complexity | Over-engineered |
| **C** | LLM-only causal reasoning | No schema change | Slow, expensive, unreliable | Rejected for performance |

## Consequences

### Positive
- Enables root-cause analysis workflows
- Supports troubleshooting and debugging
- Improves multi-hop reasoning (key benchmark gap)
- Aligns with MAGMA architecture (ACL 2026)

### Negative
- Schema migration required (new table or JSONB field)
- Extraction logic more complex (causal language detection)
- Query performance impact (bidirectional traversal)

### Neutral/Follow-ups
- Monitor extraction accuracy for causal patterns
- Consider causal summary endpoints (like community summaries)
- Evaluate need for causal confidence thresholds

## Implementation Notes

1. Add `kg_causal_relationships` table or extend `kg_relationships` with causal-specific fields
2. Update auto-extraction prompt to identify causal language
3. Add `GET /kg/causal/{entity}` endpoint with direction parameter
4. Integrate with temporal decay (causal edges expire like others)

## References

- Spec: spec-007-causal-reasoning-graph.md
- MAGMA (ACL 2026): Multi-graph with causal edges
- Honcho ADR-001: Original KG overlay
