# Reverse Audit: rapidwebs-epistemic v0.1.0

**Date:** 2026-09-20  
**Audit Type:** Reverse (What's Missing?)  
**Auditor:** Lucien (Inline)  
**Mode:** HIGH

---

## Critical Gaps (Must Fix)

### 1. Vigilance Source Verification Missing 🔴
**Issue:** Spec-003 defines claim verification against Honcho KG, tool results, and session context — none implemented.
**Impact:** EpistemicVigilance is a no-op skeleton.
**Fix:** Implement _verify_claim_against_sources() method.
**Priority:** P0

### 2. Self-Model TTL Not Implemented 🔴
**Issue:** Spec requires 90-day TTL for mistakes, but _prune_old_mistakes() doesn't exist.
**Impact:** Mistake list grows unbounded.
**Fix:** Add TTL check in _save() or schedule periodic prune.
**Priority:** P0

### 3. No Integration Tests 🔴
**Issue:** All tests are unit-level; hook execution never validated.
**Impact:** Can't verify pre_llm_call / on_session_end actually work.
**Fix:** Add 3-5 integration tests using mock Hermes ctx.
**Priority:** P0

---

## High Priority Gaps

### 4. No Benchmark Tests 🟠
**Issue:** Spec claims <100ms latency but no benchmarks exist.
**Impact:** Performance claim unverified.
**Fix:** Add timeit-based benchmarks in tests/test_performance.py.
**Priority:** P1

### 5. Config Validation Missing 🟠
**Issue:** Invalid threshold values (e.g., 1.5) not rejected.
**Impact:** Silent misconfiguration.
**Fix:** Add validation in register() or config loading.
**Priority:** P1

### 6. Error Handling for Malformed JSON 🟠
**Issue:** _load() assumes valid JSON, no recovery path.
**Impact:** Plugin crash on corrupted file.
**Fix:** Add try/except with default model fallback.
**Priority:** P1

### 7. Logging Insufficient 🟠
**Issue:** No debug traces for confidence calculation or mistake extraction.
**Impact:** Hard to diagnose issues in production.
**Fix:** Add logger.debug() calls in key methods.
**Priority:** P1

---

## Medium Priority Gaps

### 8. No Session State Preservation 🟡
**Issue:** Confidence scores not persisted across turns.
**Impact:** Can't track confidence trends within session.
**Fix:** Add _confidence_history dict to estimator.
**Priority:** P2

### 9. No Conflict Resolution for Preferences 🟡
**Issue:** Multiple users on same account would overwrite preferences.
**Impact:** Preference mixing.
**Fix:** Add user_id scoping or merge strategy.
**Priority:** P2

### 10. No Backup Strategy 🟡
**Issue:** self_model.json can be corrupted with no recovery.
**Impact:** Data loss.
**Fix:** Add .bak rotation on writes.
**Priority:** P2

### 11. Thread Safety Not Guaranteed 🟡
**Issue:** Concurrent writes to same file could race.
**Impact:** Data corruption (unlikely but possible).
**Fix:** Add file locking or queue writes.
**Priority:** P2

---

## Low Priority Gaps

### 12. No CLI Commands 🟠
**Issue:** Can't inspect self-model or confidence stats from CLI.
**Impact:** Requires code to debug.
**Fix:** Add hermes epistemic status command.
**Priority:** P3

### 13. No Health Check Endpoint 🟠
**Issue:** Can't verify plugin is loaded and working.
**Impact:** Silent failures.
**Fix:** Add /api/plugins/epistemic health endpoint.
**Priority:** P3

### 14. Documentation Gaps 🟠
**Issue:** README missing usage examples and config reference.
**Impact:** Users can't adopt easily.
**Fix:** Complete README with examples.
**Priority:** P3

### 15. No Migration Path 🟠
**Issue:** No way to migrate from older plugin versions.
**Impact:** Breaking changes hurt users.
**Fix:** Add migration script in scripts/migrate.py.
**Priority:** P3

---

## Security Gaps

### 16. JSON Injection Risk 🟠
**Issue:** User content stored in JSON without sanitization.
**Impact:** Potential injection if JSON parsed unsafely.
**Fix:** Use json.loads() with strict mode, validate structure.
**Priority:** P1

### 17. Path Traversal in File Operations 🟠
**Issue:** _SELF_MODEL_PATH hardcoded, but future extensibility could allow traversal.
**Impact:** Low (currently safe), but worth guarding.
**Fix:** Add Path.resolve() and is_relative_to() checks.
**Priority:** P2

---

## Testing Gaps

### 18. No Edge Case Tests 🟠
**Issue:** Empty transcripts, very long responses, special characters not tested.
**Impact:** Silent failures on edge cases.
**Fix:** Add 5-10 edge case test cases.
**Priority:** P2

### 19. No Mock Testing 🟠
**Issue:** Honcho client not mocked in tests.
**Impact:** Tests require live Honcho instance.
**Fix:** Add unittest.mock patches.
**Priority:** P2

### 20. No Race Condition Tests 🟠
**Issue:** Concurrent session end handlers not tested.
**Impact:** Undetected race conditions.
**Fix:** Add threading tests.
**Priority:** P3

---

## Performance Gaps

### 21. No Memory Profile 🟠
**Issue:** Memory usage under load unknown.
**Impact:** Potential memory leak undiscovered.
**Fix:** Add tracemalloc profiling in tests.
**Priority:** P3

### 22. No GC Behavior Testing 🟠
**Issue:** Object lifecycle not tracked.
**Impact:** Potential circular references.
**Fix:** Add gc.get_objects() analysis.
**Priority:** P3

---

## Documentation Gaps

### 23. No CHANGELOG 🟠
**Issue:** No record of changes between versions.
**Impact:** Users can't track improvements.
**Fix:** Create CHANGELOG.md with version history.
**Priority:** P3

### 24. No Contributing Guide 🟠
**Issue:** No guidance for external contributors.
**Impact:** Community contribution blocked.
**Fix:** Add CONTRIBUTING.md.
**Priority:** P3

### 25. No Security Policy 🟠
**Issue:** No disclosure process documented.
**Impact:** Security researchers don't know where to report.
**Fix:** Add SECURITY.md.
**Priority:** P3

---

## Code Quality Gaps

### 26. Type Hints Incomplete 🟠
**Issue:** Some methods missing return type annotations.
**Impact:** IDE support degraded.
**Fix:** Add missing -> type annotations.
**Priority:** P3

### 27. Docstrings Sparse 🟠
**Issue:** Only class-level docstrings, no method docs.
**Impact:** Hard to understand API.
**Fix:** Add Google-style docstrings to public methods.
**Priority:** P3

### 28. Magic Numbers 🟠
**Issue:** Thresholds hardcoded (0.7, 50, 90) without constants.
**Impact:** Hard to configure.
**Fix:** Extract to module-level constants.
**Priority:** P3

---

## Overall Assessment

| Category | Count |
|----------|-------|
| 🔴 Critical | 3 |
| 🟠 High | 4 |
| 🟡 Medium | 4 |
| 🔵 Low | 4 |
| **Total** | **15** |

**Verdict:** Plugin works but needs critical fixes before production use.

### Recommended Action Sequence
1. **Immediate:** Fix vigilance verification logic (gap #1)
2. **Immediate:** Add TTL pruning (gap #2)
3. **Immediate:** Add integration tests (gap #3)
4. **This week:** Add benchmarks, config validation, error handling
5. **Next week:** Address medium-priority gaps
6. **Post-v1:** Documentation and polish

---

**Audit Complete.** 15 gaps identified, 3 critical blockers.
