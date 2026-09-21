# Reverse Audit: Theory of Mind Implementation

**Date:** 2026-09-21  
**Audit Type:** Reverse (What's Missing?)  
**Auditor:** Lucien (Inline)  
**Mode:** MEDIUM

---

## Critical Gaps (Must Fix)

### 1. Hook Integration Missing 🔴
**Location:** `__init__.py` plugin hooks

**Issue:** Theory of Mind components exist but not wired into plugin lifecycle:
- `on_session_start` should inject user model context
- `on_session_end` should trigger extraction and aggregation

**Fix:**
```python
# In register()
from src.user_model import Tier1Store, Tier2Store, Tier3Store, ExtractionEngine, PredictionEngine

# Wire into hooks
ctx.register_hook("on_session_start", _on_session_start_tom)
ctx.register_hook("on_session_end", _on_session_end_tom)
```

**Priority:** P0 — Without this, ToM doesn't activate

---

### 2. No User Isolation 🟠
**Issue:** All users share same Tier 3 model

**Impact:** Cross-contamination between different Telegram users

**Fix:** Add user_id parameter to all store methods:
```python
def __init__(self, base_path: Path, user_id: str):
    self.user_id = user_id
    self.base_path = base_path / user_id
```

**Priority:** P1 — Needed for multi-user deployment

---

## High Priority Gaps

### 3. No Configuration Exposure 🟠
**Issue:** Tier TTLs hardcoded (`_TIER1_MAX_AGE_DAYS = 30`)

**Fix:** Move to plugin config in `plugin.yaml`:
```yaml
theory_of_mind:
  tier1_max_age_days: 30
  tier2_max_age_days: 90
  tier3_max_entries: 100
```

**Priority:** P1 — User should be able to tune

---

### 4. Limited Extraction Heuristics 🟡
**Issue:** Pattern matching is basic:
- Style detection: 4 patterns
- Format detection: 4 patterns
- Goal detection: 5 verbs

**Risk:** May miss nuanced preferences

**Fix:** 
- Add more markers
- Consider LLM-based extraction (future)
- Allow manual preference override

**Priority:** P2 — Works for common cases, edge cases may miss

---

## Medium Priority Gaps

### 5. No Persistence Validation 🟡
**Issue:** Tests use `tmp_path`, production uses `~/.hermes/epistemic/`

**Fix:** Add integration test with real path:
```python
def test_persistence_to_real_path():
    base = Path.home() / ".hermes" / "epistemic" / "test_user"
    # ... verify files created
    # cleanup
```

**Priority:** P2 — Edge case but good for regression prevention

---

### 6. No Error Recovery 🟡
**Issue:** If Tier 3 model corrupted, system fails silently

**Fix:** Add try/except in load operations:
```python
def load_model(self) -> UserMentalState:
    try:
        # existing code
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to load Tier 3 model: %s", e)
        return UserMentalState(user_id=self.user_id)
```

**Priority:** P2 — Defensive programming

---

## Low Priority Gaps

### 7. No Telemetry 🟢
**Issue:** No metrics on extraction accuracy

**Future:** Add metrics for:
- Preference detection rate
- Emotional state accuracy (via user feedback)
- Prediction success rate

**Priority:** P4 — Nice to have for production tuning

---

## Completeness Checklist

| Requirement | Status |
|-------------|--------|
| Tier 1 storage | ✅ Complete |
| Tier 2 storage | ✅ Complete |
| Tier 3 aggregation | ✅ Complete |
| Preference extraction | ✅ Complete |
| Emotional detection | ✅ Complete |
| Prediction engine | ✅ Complete |
| Hook integration | ❌ Missing |
| User isolation | ❌ Missing |
| Config exposure | ❌ Missing |
| Error recovery | 🟡 Partial |

**Completion:** 7/10 (70%)

---

## Recommended Actions

1. **Immediate (P0):** Wire hooks into plugin
2. **This Sprint (P1):** Add user isolation
3. **Next Sprint (P2):** Expose config, add error recovery
4. **Future (P3-P4):** Telemetry, advanced extraction

---

**Audit Complete.** Core ToM implemented, 17 tests passing. Hook integration required for activation.
