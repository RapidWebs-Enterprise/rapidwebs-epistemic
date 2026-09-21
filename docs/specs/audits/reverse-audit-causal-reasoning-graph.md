# Reverse Audit: Causal Reasoning Graph

**Date:** 2026-09-21  
**Spec:** spec-007-causal-reasoning-graph-v1.1.md  
**Auditor:** Lucien (Inline)  
**Mode:** HIGH

---

## Critical Gaps (Must Fix)

### 1. No Conflict Resolution Strategy 🔴
**Issue:** What happens when two causal claims contradict?
- Claim 1: "A caused B" (confidence 0.9, from session 1)
- Claim 2: "C caused B" (confidence 0.7, from session 2)

**Impact:** System returns ambiguous results

**Fix:** Add conflict resolution rules:
```python
def resolve_conflict(claims: list[CausalClaim]) -> CausalClaim:
    """Latest high-confidence claim wins."""
    return max(claims, key=lambda c: (c.confidence, c.created_at))
```

---

### 2. No Circular Dependency Detection 🔴
**Issue:** Causal chains could form cycles:
- A → B → C → A

**Impact:** Infinite loop in traversal

**Fix:** Add visited set to BFS:
```python
visited = set()
def traverse(entity, depth, visited):
    if entity in visited:
        return []
    visited.add(entity)
    # ... rest of traversal
```

---

## High Priority Gaps

### 3. No Causal Summary Endpoints 🟠
**Issue:** Users can't get "top causes" or "cascade analysis"

**Fix:** Add aggregation endpoints:
```
GET /v3/workspaces/{w}/kg/causal/{entity}/summary
  ?depth=3
  ?limit=10
```

### 4. No Visualization Support 🟠
**Issue:** Causal chains hard to understand without visualization

**Fix:** Add JSON export for graphviz/d3:
```json
{
  "nodes": [{"id": "A", "label": "Database full"}],
  "edges": [{"from": "A", "to": "B", "weight": 0.9}]
}
```

---

## Medium Priority Gaps

### 5. No Extraction Quality Metrics 🟡
**Issue:** Can't measure how well causal extraction works

**Fix:** Add metrics:
- Extraction accuracy (manual review)
- False positive rate
- Coverage (what % of conversations have causal claims)

### 6. No Performance Benchmarks 🟡
**Issue:** No latency targets for deep traversals

**Fix:** Add benchmarks:
- Depth 1: <50ms
- Depth 3: <200ms
- Depth 5: <500ms (hard limit)

---

## Low Priority Gaps

### 7. No Documentation Examples 🟢
**Issue:** Users don't know how to use causal queries

**Fix:** Add examples to API docs:
```bash
# Find root causes
GET /kg/causal/service_crashed?direction=incoming

# Find downstream effects
GET /kg/causal/database_full?direction=outgoing
```

### 8. No Rollback Plan 🟢
**Issue:** What if causal extraction creates bad data?

**Fix:** Add cleanup endpoint:
```
DELETE /v3/workspaces/{w}/kg/causal/{claim_id}
```

---

## Completeness Checklist

| Requirement | Status |
|-------------|--------|
| Data model | ✅ Complete |
| API endpoints | ✅ Complete |
| Extraction logic | 🟡 Partial (needs prompts) |
| Conflict resolution | ❌ Missing |
| Cycle detection | ❌ Missing |
| Performance bounds | 🟡 Partial (needs metrics) |
| Error handling | 🟡 Partial |
| Documentation | 🟢 Low priority |

**Completion:** 70%

---

## Recommended Actions

1. **Immediate (P0):** Add cycle detection to traversal algorithm
2. **This Sprint (P1):** Implement conflict resolution
3. **Next Sprint (P2):** Add extraction quality metrics
4. **Future (P3):** Visualization support

---

**Audit Complete.** Causal Reasoning Graph needs conflict resolution and cycle detection before implementation.
