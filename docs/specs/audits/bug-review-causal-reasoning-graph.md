# Bug Review: Causal Reasoning Graph

**Date:** 2026-09-21  
**Spec:** spec-007-causal-reasoning-graph-v1.1.md  
**Auditor:** Lucien (Inline)  
**Mode:** HIGH

---

## Logic Bugs

### BUG-1: BFS Doesn't Track Visited Nodes Per-Path
**Location:** traverse_causal() algorithm
**Issue:** Global visited set prevents finding all paths in DAG
```python
# Current (WRONG):
visited = {entity}  # Global

# Fixed:
visited = {entity}  # Per-path tracking needed
```
**Impact:** Misses valid causal chains
**Severity:** HIGH

---

### BUG-2: Direction Parameter Not Validated
**Location:** GET /kg/causal/{entity}
**Issue:** Invalid direction values accepted
```python
# Current:
direction: str = "both"  # No validation

# Fixed:
@validator('direction')
def validate_direction(v):
    if v not in ['outgoing', 'incoming', 'both']:
        raise ValueError('Invalid direction')
    return v
```
**Impact:** API errors or unexpected behavior
**Severity:** MEDIUM

---

### BUG-3: Max Depth Not Enforced
**Location:** traverse_causal() algorithm
**Issue:** max_depth parameter ignored
```python
# Current:
if depth > max_depth:  # max_depth from request

# Fixed:
effective_depth = min(max_depth, 5)  # Hard cap
```
**Impact:** DoS via deep traversal
**Severity:** HIGH

---

## Code Quality Issues

### ISSUE-1: No Type Hints on Return Values
```python
# Current:
async def traverse_causal(entity, direction, max_depth):

# Fixed:
async def traverse_causal(
    entity: str,
    direction: Literal['outgoing', 'incoming', 'both'],
    max_depth: int
) -> list[dict]:
```

---

### ISSUE-2: Error Messages Not User-Friendly
```python
# Current:
raise Exception("Entity not found")

# Fixed:
raise HTTPException(
    status_code=404,
    detail=f"Entity '{entity}' not found in workspace"
)
```

---

### ISSUE-3: No Logging for Traversal Stats
```python
# Add:
logger.info(
    "Causal traversal: entity=%s direction=%s depth=%d results=%d",
    entity, direction, max_depth, len(results)
)
```

---

## Security Issues

### SEC-1: No Input Sanitization
**Location:** Entity ID parameter
**Fix:** Add regex validation
```python
import re
if not re.match(r'^[a-zA-Z0-9_-]+$', entity):
    raise HTTPException(400, "Invalid entity ID format")
```

---

### SEC-2: SQL Injection Risk
**Location:** Database queries
**Fix:** Use parameterized queries
```python
# BAD:
f"SELECT * FROM kg_causal WHERE source='{entity}'"
# GOOD:
cursor.execute("SELECT * FROM kg_causal WHERE source=%s", (entity,))
```

---

## Performance Issues

### PERF-1: No Index on causal_relationships
**Issue:** Full table scan on entity lookups
**Fix:** Add indexes
```sql
CREATE INDEX idx_causal_source ON kg_causal_relationships(source_entity_id);
CREATE INDEX idx_causal_target ON kg_causal_relationships(target_entity_id);
CREATE INDEX idx_causal_valid ON kg_causal_relationships(valid_from, valid_to);
```

---

### PERF-2: Synchronous LLM Calls
**Issue:** Extraction blocks request thread
**Fix:** Make async
```python
async def extract_causal_claims(messages):
    # Use async LLM client
    response = await llm_client.complete(prompt)
```

---

## Recommended Fixes

| ID | Severity | Fix | Effort |
|----|----------|-----|--------|
| BUG-1 | HIGH | Track visited per-path | 2h |
| BUG-2 | MEDIUM | Add validator | 30m |
| BUG-3 | HIGH | Enforce hard cap | 30m |
| SEC-1 | HIGH | Add input validation | 1h |
| SEC-2 | MEDIUM | Parameterize queries | 1h |
| PERF-1 | MEDIUM | Add database indexes | 1h |

**Total estimated fix time:** ~6 hours

---

**Bug Review Complete.** 3 high severity, 3 medium severity issues found.
