---
name: causal-reasoning-graph
description: Add causal edge types to Honcho KG for bidirectional 'why' queries and troubleshooting workflows
status: proposed
created: 2026-09-21
author: Lucien (RapidWebs)
related-adrs: [ADR-006]
---

# Spec: Causal Reasoning Graph

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
- `temporal_validity: tuple[datetime, datetime]` (when causal link was valid)

#### Scenario: Causal fact extraction
- **GIVEN** conversation mentions "The service crashed because the database ran out of disk space"
- **WHEN** auto-extraction runs
- **THEN** creates causal edge: `database_full` → `service_crashed` with confidence 0.95

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
- **THEN** returns root causes with confidence scores

#### Scenario: What happened query
- **GIVEN** entity "database_full" with outgoing causal edges
- **WHEN** query `direction=outgoing`
- **THEN** returns cascading effects

### R3: Integration with Existing Components
Causal edges SHALL integrate with:
- Temporal decay (causal links expire like other edges)
- Auto-extraction (LLM identifies causal language patterns)
- Epistemic vigilance (causal claims flagged for verification)

## Non-Requirements

- Does NOT replace semantic/temporal/entity edge types
- Does NOT require real-time causal inference (batch extraction OK)
- Does NOT model complex causal networks (simple cause→effect chains)
- Does NOT persist causal edges across workspaces

## Design Notes

### Data Model
```python
class KGCausalRelationship(KGRelationship):
    """Causal edge with confidence and evidence."""
    
    cause_confidence: float = Field(ge=0.0, le=1.0)
    evidence_text: Optional[str] = None
    inferred: bool = True  # LLM-inferred vs. stated
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    
    # Reverse lookup cache (populated on query)
    _upstream_causes: list[str] = field(default_factory=list)
    _downstream_effects: list[str] = field(default_factory=list)
```

### Extraction Patterns
Causal language indicators for auto-extraction:
- "because", "due to", "caused by", "led to", "resulted in"
- "therefore", "consequently", "thus", "hence"
- Temporal sequences: "after X, Y happened"

### Query Algorithm
```python
async def traverse_causal(entity: str, direction: str, max_depth: int):
    """BFS traversal with causal edge filtering."""
    queue = [(entity, 0, [])]
    results = []
    
    while queue:
        current, depth, path = queue.pop(0)
        
        if depth > max_depth:
            continue
            
        if direction in ["outgoing", "both"]:
            causes = await get_outgoing_causal(current)
            for cause in causes:
                results.append({
                    "entity": current,
                    "relation": "caused",
                    "target": cause.entity,
                    "confidence": cause.confidence,
                    "path": path + [current]
                })
                queue.append((cause.entity, depth + 1, path + [current]))
        
        if direction in ["incoming", "both"]:
            effects = await get_incoming_causal(current)
            for effect in effects:
                results.append({
                    "entity": effect.entity,
                    "relation": "caused",
                    "target": current,
                    "confidence": effect.confidence,
                    "path": path + [current]
                })
                queue.append((effect.entity, depth + 1, path + [current]))
    
    return results
```

## Open Questions

1. Should causal edges have different temporal decay rates?
2. How to handle conflicting causal claims (A caused B vs. C caused B)?
3. Should we add causal summary endpoints (like community summaries)?

## References

- MAGMA (ACL 2026): Multi-graph architecture with causal edges
- Zep/Graphiti: Temporal knowledge graphs with invalidation
- Honcho ADR-001: Original KG overlay design
