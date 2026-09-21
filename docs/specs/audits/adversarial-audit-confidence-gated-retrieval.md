# Adversarial Audit: Confidence-Gated Retrieval

**Date:** 2026-09-21  
**Spec:** spec-008-confidence-gated-retrieval.md  
**Auditor:** Lucien (Inline)  
**Mode:** HIGH

---

## Security Vulnerabilities

### 🔴 CRITICAL: Confidence Score Manipulation
**Vector:** User crafts query to manipulate scoring
```json
{
  "query": "test",
  "min_confidence": -0.5  // Should be clamped to 0.0
}
```
**Impact:** Bypasses confidence filtering
**Fix:** Input validation
```python
min_confidence = max(0.0, min(1.0, request.min_confidence))
```

---

### 🔴 CRITICAL: DoS via Provenance Expansion
**Vector:** Query with include_provenance=true on high-cardinality data
```json
{
  "query": "*",
  "include_provenance": true,
  "top_k": 1000
}
```
**Impact:** Response size explosion, memory exhaustion
**Fix:** Cap provenance sources per conclusion
```python
max_sources_per_conclusion = 5
provenance = sources[:max_sources_per_conclusion]
```

---

### 🟠 HIGH: Source Type Injection
**Vector:** Malicious source type in conclusion
```python
conclusion.source_type = "<script>alert('xss')</script>"
```
**Impact:** XSS if provenance rendered in UI
**Fix:** Sanitize source types
```python
from markupsafe import escape
safe_type = escape(conclusion.source_type)
```

---

### 🟠 HIGH: Temporal Manipulation
**Vector:** Future timestamps to boost freshness
```python
conclusion.created_at = datetime.now() + timedelta(days=365)
```
**Impact:** Stale conclusions appear fresh
**Fix:** Clamp created_at to now
```python
conclusion.created_at = min(conclusion.created_at, datetime.now())
```

---

### 🟡 MEDIUM: Consensus Inflation
**Vector:** Duplicate sources counted as consensus
```python
sources = [
    {"type": "conversation", "id": "session_1"},
    {"type": "conversation", "id": "session_1"},  // Duplicate
]
# Consensus = 2/5 = 0.4 (inflated)
```
**Impact:** Artificially high confidence
**Fix:** Deduplicate sources
```python
unique_sources = set(s["id"] for s in sources)
consensus = min(1.0, len(unique_sources) / 5)
```

---

### 🟡 MEDIUM: Cache Poisoning
**Vector:** Pollute confidence cache with wrong scores
**Impact:** Incorrect scores served to all users
**Fix:** Cache key includes workspace
```python
cache_key = f"{workspace_id}:{conclusion_id}"
```

---

### 🟢 LOW: Weight Configuration Exposure
**Vector:** API returns weight values
**Impact:** Information disclosure
**Fix:** Don't expose internal weights in response

---

## Edge Cases

| Case | Input | Expected | Status |
|------|-------|----------|--------|
| Negative confidence | -0.5 | Clamp to 0.0 | ✅ Need validation |
| Confidence > 1.0 | 1.5 | Clamp to 1.0 | ✅ Need validation |
| Missing source type | null | Default 0.5 | ✅ Implemented |
| Empty sources list | [] | Default 0.5 | ✅ Implemented |
| Future created_at | +365 days | Clamp to now | 🟡 Needs fix |

---

## Authentication & Authorization

| Check | Status | Notes |
|-------|--------|-------|
| API key required | ✅ Inherited | Uses existing auth |
| Workspace scoping | ✅ Verified | All queries scoped |
| Read-only operation | ✅ Confirmed | No mutations |
| Config access | 🟡 Restricted | Weights not exposed |

---

## Data Integrity Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Score calculation error | 🟡 Medium | Unit tests for formula |
| Rounding errors | 🟢 Low | Use Decimal for math |
| Cache staleness | 🟡 Medium | Add cache invalidation |
| Source dedup failure | 🟠 High | Implement proper dedup |

---

## Recommended Security Fixes

1. **Immediate:** Add input validation for min_confidence
2. **Immediate:** Cap provenance sources per conclusion
3. **P1:** Sanitize source types (XSS prevention)
4. **P1:** Clamp temporal values
5. **P2:** Implement source deduplication
6. **P3:** Add cache key workspace scoping

---

**Audit Complete.** 2 critical, 2 high, 2 medium, 1 low security issues found.
