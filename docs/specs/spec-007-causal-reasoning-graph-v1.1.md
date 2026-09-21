---
name: causal-reasoning-graph
description: Add causal edge types to Honcho KG for bidirectional 'why' queries and troubleshooting workflows
status: proposed
created: 2026-09-21
updated: 2026-09-21
version: 1.1
author: Lucien (RapidWebs)
related-adrs: [ADR-006]
review-status: reviewed
---

# Spec v1.1: Causal Reasoning Graph

## Review Summary

**Changes from v1.0:**
- Added temporal validity windows to causal edges
- Clarified bidirectional query semantics
- Added integration points with existing KG endpoints
- Added performance considerations for deep traversal

## Context

Honcho's Knowledge Graph currently captures entities and relationships but lacks explicit causal modeling. When an agent asks "Why did the deployment fail?", the system cannot traverse cause-effect chains—it only knows "what" is connected, not "why."

**Problem:** No mechanism to represent or query causal relationships in the KG.

**Solution:** Add causal edge type with bidirectional inference (cause→effect and effect←cause), enabling "why" queries and troubleshooting workflows.

## Requirements

### R1: Causal Edge Type
The system SHALL add a new `KGCausalRelationship` type with:
- `cause_confidence: float` (0.0-1.0)
- `evidence_text: str` (source quote or tool result)
- `inferred: bool` (LLM-inferred vs. explicitly stated)
- `valid_from: datetime` (when causal link became true)
- `valid_to: Optional[datetime]` (when causal link ceased to be true)

#### Scenario: Causal fact extraction
- **GIVEN** conversation mentions "The service crashed because the database ran out of disk space"
- **WHEN** auto-extraction runs
- **THEN** creates causal edge: `database_full` → `service_crashed` with confidence 0.95, valid_from=now

#### Scenario: Bidirectional query
- **GIVEN** causal edge exists between two events
- **WHEN** user asks "What caused the service crash?"
- **THEN** returns upstream causes via reverse traversal
- **WHEN** user asks "What happened after the database filled?"
- **THEN** returns downstream effects via forward traversal

### R2: Causal Query Endpoints
The system SHALL expose:
```
GET /v3/workspaces/{w}/kg/causal/{entity}
  ?direction=outgoing|incoming|both
  ?max_depth=3
  ?include_provenance=true
  
POST /v3/workspaces/{w}/kg/causal/traverse
  {
    "start_entity": "database_full",
    "query_type": "why|what_happened",
    "max_depth": 3
  }
```

#### Scenario: Why query
- **GIVEN** entity "service_crashed" with incoming causal edges
- **WHEN** query `direction=incoming`
- **THEN** returns root causes with confidence scores and provenance

#### Scenario: What happened query
- **GIVEN** entity "database_full" with outgoing causal edges
- **WHEN** query `direction=outgoing`
- **THEN** returns cascading effects with temporal ordering

### R3: Integration with Existing Components
Causal edges SHALL integrate with:
- Temporal decay (causal links expire like other edges)
- Auto-extraction (LLM identifies causal language patterns)
- Epistemic vigilance (causal claims flagged for verification)
- KG context-dump endpoint (include causal chains in dumps)

## Non-Requirements

- Does NOT replace semantic/temporal/entity edge types
- Does NOT require real-time causal inference (batch extraction OK)
- Does NOT model complex causal networks (simple cause→effect chains)
- Does NOT persist causal edges across workspaces
- Does NOT require schema migration (new table or JSONB extension)

## Design Notes

### Data Model
```python
class KGCausalRelationship(KGRelationship):
    """Causal edge with confidence and evidence."""
    
    cause_confidence: float = Field(ge=0.0, le=1.0)
    evidence_text: Optional[str] = None
    inferred: bool = True  # LLM-inferred vs. stated
    valid_from: datetime
    valid_to: Optional[datetime] = None
    
    # Computed fields (not stored)
    @property
    def is_current(self) -> bool:
        return self.valid_to is None or self.valid_to > datetime.now(timezone.utc)
```

### Extraction Patterns
Causal language indicators for auto-extraction:
- "because", "due to", "caused by", "led to", "resulted in"
- "therefore", "consequently", "thus", "hence"
- Temporal sequences: "after X, Y happened", "X happened before Y"
- Conditional: "if X, then Y", "X implies Y"

### Query Algorithm
```python
async def traverse_causal(entity: str, direction: str, max_depth: int) -> list[dict]:
    """BFS traversal with causal edge filtering."""
    queue = [(entity, 0, [], "start")]
    results = []
    visited = {entity}
    
    while queue:
        current, depth, path, relation = queue.pop(0)
        
        if depth > max_depth:
            continue
        
        # Get causal edges
        if direction in ["outgoing", "both"]:
            causes = await db.get_outgoing_causal(current)
            for cause in causes:
                if cause.target not in visited:
                    visited.add(cause.target)
                    results.append({
                        "from": current,
                        "relation": "caused",
                        "to": cause.target,
                        "confidence": cause.confidence,
                        "path": path + [current],
                        "provenance": cause.evidence_text
                    })
                    queue.append((cause.target, depth + 1, path + [current], "effect"))
        
        if direction in ["incoming", "both"]:
            effects = await db.get_incoming_causal(current)
            for effect in effects:
                if effect.source not in visited:
                    visited.add(effect.source)
                    results.append({
                        "from": effect.source,
                        "relation": "caused",
                        "to": current,
                        "confidence": effect.confidence,
                        "path": path + [current],
                        "provenance": effect.evidence_text
                    })
                    queue.append((effect.source, depth + 1, path + [current], "cause"))
    
    return results
```

## Performance Considerations

| Operation | Complexity | Mitigation |
|-----------|------------|------------|
| Deep traversal (depth > 5) | O(b^d) where b=branches | Enforce max_depth=5 limit |
| Concurrent causal queries | DB lock contention | Read-only queries, connection pooling |
| Causal extraction LLM calls | Latency | Batch extraction, async processing |

## Open Questions

1. Should causal edges have different temporal decay rates?
2. How to handle conflicting causal claims (A caused B vs. C caused B)?
3. Should we add causal summary endpoints (like community summaries)?
4. How to visualize causal chains in TUI/desktop?

## References

- MAGMA (ACL 2026): Multi-graph architecture with causal edges
- Zep/Graphiti: Temporal knowledge graphs with invalidation
- Honcho ADR-001: Original KG overlay design
- Honcho SPEC-001: KG Overlay specification
