# Adversarial Audit: rapidwebs-epistemic v0.1.0

**Date:** 2026-09-20  
**Audit Type:** Adversarial (Security + Edge Cases)  
**Auditor:** Lucien (Inline)  
**Mode:** HIGH

---

## Security Attack Vectors

### 1. Path Traversal via Session Data

**Risk:** 🔴 CRITICAL

User input flows into self_model.json without sanitization. If session transcript contains `../` sequences, they could be stored and potentially used in future path operations.

**Evidence:**
```python
# __init__.py line ~280
self.data["past_mistakes"].append({
    "type": "self_correction",
    "content": content[:200],  # Raw user content
    "timestamp": ...
})
```

**Exploit Scenario:**
1. User sends message with content: `"I think we should delete /etc/passwd via ../.."
2. Agent records this as "mistake"
3. Future JSON parse could be manipulated if content isn't sanitized

**Mitigation:**
- Sanitize content with `json.dumps()` which escapes special chars
- Validate path components don't contain `..`
- Use Path.resolve() + is_relative_to() checks

**Status:** ⚠️ PARTIAL — JSON serialization provides some escaping, but explicit validation missing

---

### 2. JSON Injection via Malformed Input

**Risk:** 🟠 HIGH

If self_model.json becomes corrupted (partial write, disk error), plugin crashes on load.

**Evidence:**
```python
# __init__.py line ~240
content = self.path.read_text(encoding="utf-8")
return json.loads(content)  # No error handling
```

**Exploit Scenario:**
1. Plugin writes partial JSON during crash
2. Next session load fails with JSONDecodeError
3. Plugin silently fails, no self-model loaded

**Mitigation:**
- Add try/except around json.loads()
- Backup corrupted file before recreating
- Log warning for operator awareness

**Status:** ❌ NOT IMPLEMENTED — Will crash on malformed JSON

---

### 3. Race Condition on Concurrent Writes

**Risk:** 🟠 HIGH

Two sessions ending simultaneously could corrupt self_model.json.

**Evidence:**
```python
# Both sessions read, modify, write simultaneously
content = self.path.read_text()  # Session A reads
content = self.path.read_text()  # Session B reads (same content)
# Session A writes modified content
# Session B writes modified content (overwrites A's changes)
```

**Exploit Scenario:**
1. Session 1 and Session 2 both end within same second
2. Both read same JSON
3. Both write back with their modifications
4. One session's changes lost (last write wins)

**Mitigation:**
- File locking with fcntl.flock()
- Or accept data loss (single-writer assumption documented)
- Or use atomic append instead of read-modify-write

**Status:** ⚠️ KNOWN LIMITATION — No locking implemented

---

### 4. Resource Exhaustion via Mistake Accumulation

**Risk:** 🟡 MEDIUM

No TTL pruning means past_mistakes list grows unbounded.

**Evidence:**
```python
# __init__.py line ~285
self.data["past_mistakes"].extend(mistakes)
# No pruning logic exists
```

**Exploit Scenario:**
1. Agent has 1000 sessions over 6 months
2. Each session adds 5 mistakes
3. past_mistakes list has 5000 entries
4. JSON file grows to 500KB+
5. Load time increases, memory pressure rises

**Mitigation:**
- Implement TTL pruning (as identified in reverse audit)
- Cap at max entries (e.g., 50)
- Archive old mistakes to separate file

**Status:** ❌ NOT IMPLEMENTED — Unbounded growth possible

---

### 5. Denial of Service via Malicious Transcript

**Risk:** 🟡 MEDIUM

Adversarial user could craft transcript to cause infinite loops or excessive computation.

**Evidence:**
```python
# Confidence estimation loops through phrases
for phrase in self.UNCERTAINTY_PHRASES:
    if phrase in text_lower:
        count += 1
```

**Exploit Scenario:**
1. User sends message with 1000 repetitions of "I'm not sure"
2. String scanning becomes slow
3. Blocks event loop for extended period

**Mitigation:**
- Cap text length before analysis (e.g., first 500 chars)
- Add timeout to estimation
- Use more efficient search (any() with generator)

**Status:** ⚠️ LOW RISK — Unlikely in practice, but no defensive capping

---

### 6. Information Leakage via Error Messages

**Risk:** 🟡 MEDIUM

Error traces could expose internal paths or file structures.

**Evidence:**
```python
# Potential exception leakage
except json.JSONDecodeError as e:
    logger.warning(f"Failed: {e}")  # Could expose file paths
```

**Exploit Scenario:**
1. Malformed JSON triggers exception
2. Error logged with full traceback
3. Internal directory structure exposed in logs

**Mitigation:**
- Sanitize error messages
- Log to file only, not stdout
- Use generic error messages for external visibility

**Status:** ⚠️ PARTIAL — Logging exists but not sanitized

---

## Edge Case Analysis

### 1. Empty Transcript Handling

**Scenario:** Session with no tool calls, single message

**Expected:** confidence = 0.5 (neutral baseline)

**Actual:** ⚠️ Returns 0.5 based on default weights — acceptable

---

### 2. Very Long Response (>10K chars)

**Scenario:** Agent generates extremely long response

**Expected:** Should not crash, should cap analysis

**Actual:** ❌ No length capping — could cause memory issues

---

### 3. Special Characters in Content

**Scenario:** Response contains Unicode, emojis, control chars

**Expected:** Should serialize safely to JSON

**Actual:** ✅ json.dumps() handles this correctly

---

### 4. Concurrent Session Access

**Scenario:** Two gateway instances write to same file

**Expected:** Should handle gracefully

**Actual:** ❌ Race condition possible, last write wins

---

### 5. Disk Full During Write

**Scenario:** Disk fills up during atomic write

**Expected:** Should not corrupt existing file

**Actual:** ⚠️ Temp file created, original intact, but temp leaked

---

## Attack Surface Summary

| Vector | Severity | Status | Fix Required |
|--------|----------|--------|--------------|
| Path traversal | 🔴 Critical | Partial | Add validation |
| JSON injection | 🟠 High | ❌ Missing | Add error handling |
| Race condition | 🟠 High | ⚠️ Known | Add locking or docs |
| Resource exhaustion | 🟡 Medium | ❌ Missing | Add TTL pruning |
| DoS via transcript | 🟡 Medium | ⚠️ Low risk | Add length caps |
| Info leakage | 🟡 Medium | ⚠️ Partial | Sanitize errors |

---

## Recommendations

### Immediate (Before V1)
1. Add try/except around JSON loads with fallback
2. Implement mistake TTL pruning (90-day expiry)
3. Add input length capping (500 chars for analysis)

### Short-term (V1.1)
4. Add file locking for concurrent write safety
5. Sanitize error messages
6. Add path validation for future extensions

### Long-term (V2.0)
7. Consider SQLite instead of JSON for concurrent access
8. Add authentication for self-model read/write
9. Implement incremental updates to avoid full rewrite

---

**Audit Complete.** 6 attack vectors identified, 2 critical, 2 high, 2 medium.
