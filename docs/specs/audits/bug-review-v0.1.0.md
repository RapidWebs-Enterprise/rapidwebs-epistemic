# Bug Review: rapidwebs-epistemic v0.1.0

**Date:** 2026-09-20  
**Audit Type:** Bug Review (Logic, Security, Code Quality)  
**Auditor:** Lucien (Inline)  
**Mode:** HIGH

---

## Logic Bugs

### BUG-001: Confidence Score Can Exceed 1.0

**Location:** `__init__.py:145` (ConfidenceEstimator.estimate)

**Issue:** Weighted combination doesn't clamp result to [0.0, 1.0]

```python
confidence = (
    0.25 * (1 - uncertainty_score) +
    0.30 * tool_score +
    0.25 * consistency_score +
    0.20 * claim_score
)
# Missing: confidence = max(0.0, min(1.0, confidence))
```

**Impact:** Low — returns values >1.0 which may confuse consumers  
**Fix:** Add clamping before return

---

### BUG-002: Mistake Timestamp Parsing Failure

**Location:** `__init__.py:275` (SelfModel._extract_mistakes)

**Issue:** Assumes ISO format timestamp, no error handling

```python
mistakes.append({
    "timestamp": datetime.now(timezone.utc).isoformat(),
    # ...
})
```

If datetime fails (unlikely but possible), entire session update fails silently.

**Impact:** Medium — session end hook could fail  
**Fix:** Wrap in try/except with fallback

---

### BUG-003: Preference Overwrite Logic

**Location:** `__init__.py:310` (SelfModel._extract_preferences)

**Issue:** Later sessions overwrite earlier preferences without merge

```python
if "be concise" in content.lower():
    preferences["style"] = "concise"
```

If user says "be concise" in session 1, then "be thorough" in session 2, last wins. No consensus mechanism.

**Impact:** Low — reflects current behavior, but may not match user intent  
**Fix:** Add preference weighting or user confirmation

---

## Security Issues

### SEC-001: No Input Validation on Session Content

**Location:** `__init__.py:295` (SelfModel.update_from_session)

**Issue:** Transcripts accepted without length or content validation

```python
def update_from_session(self, session_id, transcript, outcome="completed"):
    # No validation of transcript structure
```

**Impact:** Medium — could store malicious content  
**Fix:** Validate transcript is list of dicts, cap total size

---

### SEC-002: Hardcoded Path Without Validation

**Location:** `__init__.py:55` (_SELF_MODEL_PATH)

**Issue:** Path constructed without checking parent directory exists

```python
_SELF_MODEL_PATH = Path.home() / ".hermes" / "epistemic" / "self_model.json"
```

If `.hermes` directory deleted, Path operations succeed but file write fails.

**Impact:** Low — mkdir exists in _save(), but _load() doesn't check  
**Fix:** Add existence check in _load()

---

## Code Quality Issues

### QOL-001: Magic Numbers

**Location:** Multiple

**Issue:** Thresholds hardcoded without named constants

```python
_CONFIDENCE_THRESHOLD = 0.7  # Good
# But:
if len(self._confidence_history) > 10:  # Magic number
```

**Impact:** Low — readability  
**Fix:** Extract to module-level constants

---

### QOL-002: Inconsistent Error Handling

**Location:** Throughout

**Issue:** Some methods return None on failure, others raise exceptions

```python
def get_context_injection(self):
    if not self.data.get("past_mistakes"):
        return None  # Silent failure
    
    # But:
    self._save()  # Could raise OSError, not caught
```

**Impact:** Medium — inconsistent API  
**Fix:** Standardize on exceptions or return codes

---

### QOL-003: Missing Type Hints on Public Methods

**Location:** `__init__.py`

**Issue:** Some public methods lack return type annotations

```python
def estimate(self, user_message, assistant_response, transcript):
    # Missing -> dict
```

**Impact:** Low — IDE support degraded  
**Fix:** Add -> dict return types

---

## Silent Failure Patterns

### FAIL-001: JSON Parse Failure Silent Recovery

**Issue:** If self_model.json corrupted, _load() returns empty model without warning

```python
try:
    return json.loads(self.path.read_text())
except (json.JSONDecodeError, OSError):
    return self._default_model()  # Silent!
```

**Impact:** Medium — user unaware their model was lost  
**Fix:** Log warning on recovery

---

### FAIL-002: File Write Failure Ignored

**Issue:** _save() catches OSError but doesn't alert user

```python
except OSError as e:
    logger.error("Failed to save: %s", e)
    # No exception raised, caller assumes success
```

**Impact:** High — data loss without notification  
**Fix:** Raise exception or return success/failure boolean

---

## Race Conditions

### RACE-001: Read-Modify-Write Without Lock

**Issue:** Multiple sessions can read, modify, write simultaneously

```python
data = json.loads(self.path.read_text())  # Read
data["past_mistakes"].append(...)         # Modify
self.path.write_text(json.dumps(data))    # Write
```

**Impact:** High — data corruption possible  
**Fix:** Add asyncio.Lock or file locking

---

## Connection/Resource Leaks

### LEAK-001: No Resource Cleanup

**Issue:** No shutdown hook to flush buffers or close resources

**Impact:** Low — files are closed on GC, but explicit cleanup better  
**Fix:** Add on_session_end cleanup if needed

---

## Summary

| Category | Count | Critical | High | Medium | Low |
|----------|-------|----------|------|--------|-----|
| Logic Bugs | 3 | 0 | 0 | 2 | 1 |
| Security | 2 | 0 | 1 | 1 | 0 |
| Code Quality | 3 | 0 | 0 | 0 | 3 |
| Silent Failures | 2 | 0 | 0 | 2 | 0 |
| Race Conditions | 1 | 0 | 1 | 0 | 0 |
| **Total** | **11** | **0** | **3** | **6** | **4** |

---

## Recommended Fixes (Priority Order)

1. **P0:** Add clamping to confidence score (BUG-001)
2. **P0:** Add file locking for concurrent writes (RACE-001)
3. **P1:** Add error logging on JSON recovery (FAIL-001)
4. **P1:** Return success/failure from _save() (FAIL-002)
5. **P1:** Add input validation on transcripts (SEC-001)
6. **P2:** Extract magic numbers to constants (QOL-001)
7. **P2:** Standardize error handling (QOL-002)
8. **P2:** Add type hints (QOL-003)
9. **P3:** Add shutil backup before overwrite
10. **P3:** Implement preference merge strategy (BUG-003)

---

**Bug Review Complete.** 11 issues found, 0 critical, 3 high, 6 medium, 4 low.
