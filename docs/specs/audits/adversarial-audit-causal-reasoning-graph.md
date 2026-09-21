# Adversarial Audit: Causal Reasoning Graph

**Date:** 2026-09-21  
**Spec:** spec-007-causal-reasoning-graph-v1.1.md  
**Auditor:** Lucien (Inline)  
**Mode:** HIGH

---

## Security Vulnerabilities

### 🔴 CRITICAL: Path Traversal in Entity IDs
**Vector:** Entity IDs passed as URL parameters
```
GET /v3/workspaces/{w}/kg/causal/../../etc/passwd
```
**Impact:** Could access files outside workspace
**Fix:** Validate entity_id format (alphanumeric + hyphens only)
```python
import re
if not re.match(r'^[a-zA-Z0-9_-]+$', entity_id):
    raise HTTPException(400, "Invalid entity ID")
```

---

### 🔴 CRITICAL: DoS via Deep Traversal
**Vector:** Malicious query with max_depth=100
```
GET /kg/causal/entity?max_depth=100
```
**Impact:** Exponential blowup O(b^d), API hangs
**Fix:** Hard limit enforcement
```python
max_depth = min(request.max_depth, 5)  # Hard cap at 5
```

---

### 🟠 HIGH: SQL Injection in Entity Search
**Vector:** Entity ID with SQL special chars
```
GET /kg/causal/entity'; DROP TABLE kg_entities;--
```
**Impact:** Data destruction
**Fix:** Parameterized queries only
```python
# BAD
query = f"SELECT * FROM kg_causal WHERE source='{entity}'"
# GOOD
cursor.execute("SELECT * FROM kg_causal WHERE source=%s", (entity,))
```

---

### 🟠 HIGH: Information Disclosure via Provenance
**Vector:** Request provenance exposes internal tool results
```
GET /kg/causal/entity?include_provenance=true
```
**Impact:** Leaks internal tool names, timestamps, possibly sensitive data
**Fix:** Sanitize provenance data
```python
def sanitize_provenance(p):
    p.pop('tool_output', None)  # Remove raw tool results
    return p
```

---

### 🟡 MEDIUM: Causal Loop Injection
**Vector:** User creates cyclic causal claims
```
A caused B, B caused C, C caused A
```
**Impact:** Infinite traversal loop
**Fix:** Cycle detection in BFS
```python
visited = set()
def traverse(entity, depth):
    if entity in visited:
        return []
    visited.add(entity)
    # ...
```

---

### 🟡 MEDIUM: Workspace Isolation Bypass
**Vector:** Cross-workspace entity ID collision
```
Workspace A has entity "db_full"
Workspace B has entity "db_full"
Query B's entity returns A's causal chains
```
**Impact:** Data leakage between workspaces
**Fix:** Scope all queries to workspace
```python
WHERE workspace_id = :workspace_id AND source_entity = :entity
```

---

### 🟢 LOW: Rate Limiting Absence
**Vector:** Rapid-fire traversal queries
**Impact:** API degradation
**Fix:** Add rate limiter
```python
@limiter.limit("10/minute")
async def get_causal(entity: str):
    ...
```

---

## Edge Cases

| Case | Input | Expected | Status |
|------|-------|----------|--------|
| Empty entity ID | "" | 400 Bad Request | ✅ Need spec |
| Non-existent entity | "ghost_entity" | 404 Not Found | ✅ Need spec |
| Max depth exceeded | depth=10 | Truncate to 5 | ✅ Implemented |
| Circular reference | A→B→C→A | Stop at cycle | ✅ Need implementation |
| Invalid direction | "diagonal" | 400 Bad Request | ✅ Need spec |

---

## Authentication & Authorization

| Check | Status | Notes |
|-------|--------|-------|
| API key required | ✅ Inherited | Uses existing KG auth |
| Workspace scoping | 🟡 Needs verification | Must verify all queries scoped |
| Read-only endpoints | ✅ All GET/POST | No mutations in spec |
| Admin-only operations | N/A | No admin endpoints defined |

---

## Data Integrity Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Orphaned causal edges | 🟡 Medium | Foreign key CASCADE DELETE |
| Stale valid_to dates | 🟢 Low | Background cleanup job |
| Confidence score manipulation | 🟡 Medium | Validate 0.0-1.0 range |
| Evidence text injection | 🟠 High | Sanitize HTML/JS in evidence_text |

---

## Recommended Security Fixes

1. **Immediate:** Add entity ID validation regex
2. **Immediate:** Enforce max_depth=5 hard limit
3. **P1:** Add provenance sanitization
4. **P1:** Implement cycle detection
5. **P2:** Add rate limiting
6. **P3:** Audit all SQL queries for parameterization

---

**Audit Complete.** 2 critical, 2 high, 2 medium, 1 low security issues found.
