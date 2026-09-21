# Reverse Audit: Confidence-Gated Retrieval

**Date:** 2026-09-21  
**Spec:** spec-008-confidence-gated-retrieval.md  
**Auditor:** Lucien (Inline)  
**Mode:** HIGH

---

## Critical Gaps (Must Fix)

### 1. No Handling for Missing Source Type 🔴
**Issue:** What if conclusion has source_type not in the mapping?

**Current spec:**
```python
source_scores = {
    "tool_result": 1.0,
    "conversation": 0.7,
    "speculation": 0.3,
    "external_api": 0.9
}
```

**Problem:** Unknown source types get KeyError

**Fix:** Add default:
```python
source_score = source_scores.get(conclusion.source_type, 0.5)
```

---

### 2. No Confidence Score Caching Strategy 🔴
**Issue:** Scores computed on every query = redundant computation

**Impact:** Unnecessary LLM/embedding calls if sources change

**Fix:** Add caching:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_confidence_score(conclusion_id: str) -> float:
    # Compute and cache
```

---

## High Priority Gaps

### 3. No Weight Tuning Interface 🟠
**Issue:** Weights hardcoded, can't adjust for different workspaces

**Fix:** Add config:
```yaml
retrieval.confidence.weights:
  source: 0.4
  freshness: 0.3
  consensus: 0.3
```

### 4. No Confidence Distribution Metrics 🟠
**Issue:** Can't monitor if filtering is too aggressive

**Fix:** Add stats to response:
```json
{
  "retrieval_stats": {
    "total_matched": 47,
    "filtered_by_confidence": 27,
    "avg_confidence": 0.72,
    "min_returned": 0.51
  }
}
```

---

## Medium Priority Gaps

### 5. No Handling for Empty Sources 🟡
**Issue:** What if conclusion has no sources?

**Current:** Falls through to default 0.5

**Fix:** Explicit handling:
```python
if not conclusion.sources:
    return 0.5  # Unknown = neutral
```

### 6. No Staleness Detection for Contradictions 🟡
**Issue:** Old contradictions not cleaned up

**Fix:** Add TTL to contradictions:
```python
contradiction.expires_at = datetime.now() + timedelta(days=30)
```

---

## Low Priority Gaps

### 7. No A/B Testing Framework 🟢
**Issue:** Can't test different weight configurations

**Fix:** Add experiment tracking:
```python
# Track which weight config performed best
experiment_tracker.record(weights, conversion_rate)
```

### 8. No Manual Confidence Override 🟢
**Issue:** Users can't mark conclusions as definitely true/false

**Fix:** Add admin endpoint:
```
PATCH /v3/workspaces/{w}/conclusions/{id}/confidence
  {"manual_score": 0.95, "reason": "Verified by admin"}
```

---

## Completeness Checklist

| Requirement | Status |
|-------------|--------|
| Scoring formula | ✅ Complete |
| API parameters | ✅ Complete |
| Response format | ✅ Complete |
| Error handling | 🟡 Partial |
| Caching strategy | ❌ Missing |
| Weight config | 🟡 Partial |
| Metrics | 🟡 Partial |

**Completion:** 75%

---

## Recommended Actions

1. **Immediate (P0):** Add default for unknown source types
2. **This Sprint (P1):** Implement caching layer
3. **Next Sprint (P2):** Add weight configuration
4. **Future (P3):** A/B testing framework

---

**Audit Complete.** Confidence-Gated Retrieval needs error handling fixes before implementation.
