---
title: "ADR-006: Causal Reasoning Graph for Honcho KG"
description: "Decision to add causal edge types with bidirectional inference for troubleshooting and 'why' queries"
category: architecture
tags:
  - honcho
  - knowledge-graph
  - causal-reasoning
version: 1.1
---

# ADR-006: Causal Reasoning Graph

**Status**: Proposed  
**Date**: 2026-09-21  
**Updated**: 2026-09-21  
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
- Temporal validity windows (valid_from, valid_to)

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
- Backward compatible (optional feature)

### Negative
- Schema migration required (new table or JSONB field)
- Extraction logic more complex (causal language detection)
- Query performance impact (bidirectional traversal)
- Increased storage for causal edges

### Neutral/Follow-ups
- Monitor extraction accuracy for causal patterns
- Consider causal summary endpoints (like community summaries)
- Evaluate need for causal confidence thresholds
- Track query latency for deep traversals

## Implementation Notes

1. **Schema**: Add `kg_causal_relationships` table OR extend `kg_relationships` with causal-specific JSONB fields
2. **Migration**: Backfill existing relationships as causal if confidence > 0.8
3. **Extraction**: Update auto-extraction prompt to identify causal language
4. **Endpoints**: Add `GET /kg/causal/{entity}` and `POST /kg/causal/traverse`
5. **Integration**: Wire into temporal decay, epistemic vigilance, context-dump

## Migration Plan

```sql
-- Option 1: New table
CREATE TABLE kg_causal_relationships (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    source_entity_id TEXT NOT NULL,
    target_entity_id TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    evidence_text TEXT,
    inferred BOOLEAN DEFAULT true,
    valid_from TIMESTAMPTZ NOT NULL,
    valid_to TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    FOREIGN KEY (source_entity_id) REFERENCES kg_entities(id),
    FOREIGN KEY (target_entity_id) REFERENCES kg_entities(id)
);

-- Option 2: JSONB extension (preferred for minimal migration)
ALTER TABLE kg_relationships ADD COLUMN causal_data JSONB;
-- Store causal-specific fields in causal_data when type='causal'
```

## References

- Spec: spec-007-causal-reasoning-graph.md (v1.1)
- MAGMA (ACL 2026): Multi-graph with causal edges
- Honcho ADR-001: Original KG overlay
- Honcho SPEC-001: KG Overlay specification
