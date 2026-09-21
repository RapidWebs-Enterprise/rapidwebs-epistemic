# Bug Review: Confidence-Gated Retrieval

**Date:** 2026-09-21  
**Spec:** spec-008-confidence-gated-retrieval.md  
**Auditor:** Lucien (Inline)  
**Mode:** HIGH

---

## Logic Bugs

### BUG-1: Floating Point Precision
**Location:** calculate_confidence()
**Issue:** Floating point rounding errors
```python
# Current:
confidence = 0.4 * source_score + 0.3 * freshness + 0.3 * consensus

# Fixed:
from decimal import Decimal
confidence = Decimal('0.4') * source_score + Decimal('0.3') * freshness + Decimal('0.3') * consensus
```
**Impact:** Inconsistent scores across runs
**Severity:** LOW

---

### BUG-2: Division by Zero in Consensus
**Location:** calculate_confidence()
**Issue:** If source_count = 0
```python
# Current:
consensus = min(1.0, source_count / 5)

# Fixed:
consensus = min(1.0, source_count / 5) if source_count > 0 else 0.0
```
**Impact:** ZeroDivisionError crash
**Severity:** MEDIUM

---

### BUG-3: Temporal Decay Formula Error
**Location:** calculate_confidence()
**Issue:** Wrong decay constant
```python
# Current (WRONG):
freshness = math.exp(-age_days * ln(2) / HALF_LIFE_DAYS)

# Fixed (CORRECT):
freshness = math.exp(-age_days * 0.693 / HALF_LIFE_DAYS)
# Or simpler:
freshness = 0.5 ** (age_days / HALF_LIFE_DAYS)
```
**Impact:** Incorrect freshness scores
**Severity:** HIGH

---

## Code Quality Issues

### ISSUE-1: Magic Numbers
```python
# Current:
source_scores = {
    "tool_result": 1.0,
    "conversation": 0.7,
    "speculation": 0.3,
}

# Fixed:
SOURCE_CREDIBILITY = {
    "tool_result": 1.0,
    "external_api": 0.9,
    "conversation": 0.7,
    "speculation": 0.3,
}
DEFAULT_CREDIBILITY = 0.5
```

---

### ISSUE-2: No Docstrings
```python
# Current:
def calculate_confidence(conclusion):

# Fixed:
def calculate_confidence(conclusion: Conclusion) -> float:
    """Calculate confidence score for a conclusion.
    
    Args:
        conclusion: The conclusion to score
        
    Returns:
        Float between 0.0 and 1.0
    """
```

---

## Security Issues

### SEC-1: Confidence Score Injection
**Issue:** Client can manipulate scores via crafted source types
```python
# Malicious source type:
{"type": "tool_result", "id": "admin_verified"}
# Gets score 1.0 artificially
```
**Fix:** Whitelist source types
```python
ALLOWED_SOURCE_TYPES = {"tool_result", "conversation", "speculation", "external_api"}
if source.type not in ALLOWED_SOURCE_TYPES:
    source.score = DEFAULT_CREDIBILITY
```

---

### SEC-2: Response Size Limit
**Issue:** Provenance can be arbitrarily large
```python
# Fix:
MAX_PROVENANCE_SOURCES = 5
provenance = sources[:MAX_PROVENANCE_SOURCES]
```

---

## Performance Issues

### PERF-1: Repeated Calculations
**Issue:** Same conclusion scored multiple times
```python
# Fix: Add caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_confidence_cached(conclusion_id: str) -> float:
    conclusion = db.get(conclusion_id)
    return calculate_confidence(conclusion)
```

---

### PERF-2: N+1 Source Queries
**Issue:** Query sources for each conclusion separately
```python
# Current (WRONG):
for conclusion in conclusions:
    sources = db.get_sources(conclusion.id)  # N queries

# Fixed (CORRECT):
conclusion_ids = [c.id for c in conclusions]
sources_map = db.get_sources_batch(conclusion_ids)  # 1 query
```

---

## Recommended Fixes

| ID | Severity | Fix | Effort |
|----|----------|-----|--------|
| BUG-1 | LOW | Use Decimal | 30m |
| BUG-2 | MEDIUM | Add zero check | 15m |
| BUG-3 | HIGH | Fix decay formula | 30m |
| SEC-1 | MEDIUM | Whitelist source types | 1h |
| SEC-2 | LOW | Cap provenance | 15m |
| PERF-1 | MEDIUM | Add caching | 1h |
| PERF-2 | HIGH | Batch queries | 2h |

**Total estimated fix time:** ~5 hours

---

**Bug Review Complete.** 1 high, 2 medium, 4 low severity issues found.
