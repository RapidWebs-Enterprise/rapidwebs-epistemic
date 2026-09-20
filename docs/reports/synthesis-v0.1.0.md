# Synthesis: rapidwebs-epistemic v0.1.0

**Date:** 2026-09-20  
**Audits:** Forward + Reverse  
**Mode:** HIGH  
**Status:** READY FOR SIGN-OFF

---

## Audit Summary

| Audit | Gaps Found | Critical | High | Medium | Low |
|-------|------------|----------|------|--------|-----|
| Forward | 7 | 2 | 3 | 2 | 0 |
| Reverse | 15 | 3 | 4 | 4 | 4 |
| **Total** | **22** | **5** | **7** | **6** | **4** |

---

## Critical Fixes Required (P0)

### 1. Implement Vigilance Source Verification
**From:** Forward audit (Spec-003 incomplete), Reverse audit (#1)

**Current State:** EpistemicVigilance class exists but verification logic is placeholder.

**Required Implementation:**
```python
def _verify_claim_against_sources(self, claim: str) -> dict:
    """Check claim against Honcho KG, tool results, and session context."""
    results = {
        "claim": claim,
        "status": "unverified",
        "sources_checked": [],
        "evidence": []
    }
    
    # 1. Check Honcho KG
    honcho_results = self._query_honcho_kg(claim)
    if honcho_results:
        results["sources_checked"].append("honcho_kg")
        if honcho_results.confirmed:
            results["status"] = "verified"
            results["evidence"].append(honcho_results.source)
    
    # 2. Check recent tool results
    tool_results = self._check_tool_results(claim)
    if tool_results:
        results["sources_checked"].append("tool_results")
        # ... similar logic
    
    # 3. Check session context
    context_results = self._check_session_context(claim)
    if context_results:
        results["sources_checked"].append("session_context")
        # ... similar logic
    
    return results
```

**Effort:** 4 hours  
**Risk:** Medium (requires Honcho client integration)

---

### 2. Add TTL Pruning for Self-Model
**From:** Forward audit (Spec-002 partial), Reverse audit (#2)

**Current State:** Mistakes append indefinitely, no expiration.

**Required Implementation:**
```python
def _prune_old_mistakes(self):
    """Remove mistakes older than 90 days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    original_count = len(self.data["past_mistakes"])
    
    self.data["past_mistakes"] = [
        m for m in self.data["past_mistakes"]
        if datetime.fromisoformat(m["timestamp"]) > cutoff
    ]
    
    pruned = original_count - len(self.data["past_mistakes"])
    if pruned > 0:
        self._save()
        logger.info(f"Pruned {pruned} old mistakes")
```

**Effort:** 30 minutes  
**Risk:** Low

---

### 3. Add Integration Tests
**From:** Reverse audit (#3)

**Current State:** Only unit tests exist (14 total).

**Required Tests:**
```python
def test_pre_llm_call_injects_low_confidence():
    """Verify hook injects context when confidence < threshold."""
    # Mock transcript with uncertainty markers
    # Call hook
    # Assert context injected
    
def test_on_session_end_updates_self_model():
    """Verify session end extracts mistakes and preferences."""
    # Create mock transcript
    # Call hook
    # Assert self_model.json updated
    
def test_on_session_start_loads_self_model():
    """Verify session start loads and injects self-model."""
    # Create self_model.json
    # Call hook
    # Assert context injected
```

**Effort:** 2 hours  
**Risk:** Low

---

## High Priority Fixes (P1)

### 4. Add Benchmark Tests
**From:** Reverse audit (#4)

**Required:**
```python
def test_confidence_estimation_latency():
    """Verify <100ms performance claim."""
    import time
    start = time.perf_counter()
    
    estimator = ConfidenceEstimator()
    for _ in range(100):
        estimator.estimate("test", "response", [])
    
    elapsed = time.perf_counter() - start
    avg_ms = (elapsed / 100) * 1000
    
    assert avg_ms < 100, f"Average latency {avg_ms:.2f}ms exceeds 100ms"
```

**Effort:** 1 hour  
**Risk:** Low

---

### 5. Add Config Validation
**From:** Reverse audit (#5)

**Required:**
```python
def _validate_config(self, config: dict) -> bool:
    """Validate plugin configuration."""
    errors = []
    
    threshold = config.get("confidence_threshold", 0.7)
    if not 0.0 <= threshold <= 1.0:
        errors.append("confidence_threshold must be 0.0-1.0")
    
    if errors:
        logger.error(f"Config validation failed: {errors}")
        return False
    return True
```

**Effort:** 30 minutes  
**Risk:** Low

---

### 6. Add Error Handling for Malformed JSON
**From:** Reverse audit (#6)

**Required:**
```python
def _load(self) -> dict:
    """Load self-model from disk with error recovery."""
    if not self.path.exists():
        return self._default_model()
    
    try:
        content = self.path.read_text(encoding="utf-8")
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.warning(f"Corrupted self-model, recreating: {e}")
        # Backup corrupted file
        backup = self.path.with_suffix(".json.corrupted")
        self.path.rename(backup)
        return self._default_model()
    except OSError as e:
        logger.error(f"Failed to load self-model: {e}")
        return self._default_model()
```

**Effort:** 30 minutes  
**Risk:** Low

---

### 7. Add Debug Logging
**From:** Reverse audit (#7)

**Required:**
```python
# In ConfidenceEstimator.estimate()
logger.debug(f"Confidence factors: {factors}")
logger.debug(f"Final confidence: {confidence:.2f}")

# In SelfModel.update_from_session()
logger.debug(f"Extracted {len(mistakes)} mistakes, {len(prefs)} preferences")
```

**Effort:** 30 minutes  
**Risk:** Low

---

## Revised Implementation Plan

### Phase 1: Critical Fixes (1 day)
- [ ] Implement vigilance source verification (4h)
- [ ] Add TTL pruning (30m)
- [ ] Add integration tests (2h)

### Phase 2: High Priority (1 day)
- [ ] Add benchmark tests (1h)
- [ ] Add config validation (30m)
- [ ] Add error handling (30m)
- [ ] Add debug logging (30m)

### Phase 3: Polish (0.5 day)
- [ ] Complete README with examples
- [ ] Add type hints to all public methods
- [ ] Final test run and cleanup

**Total Estimated Effort:** 12 hours  
**Timeline:** 2 days

---

## Updated File Manifest

| File | Lines | Status |
|------|-------|--------|
| `__init__.py` | ~400 | Needs vigilance completion |
| `tests/test_epistemic.py` | ~250 | Needs integration + benchmarks |
| `docs/specs/spec-00*.md` | 5 docs | Complete |
| `docs/adrs/adr-00*.md` | 5 docs | Complete |
| `docs/plans/*.md` | 1 doc | Complete |
| `docs/research/*.md` | 4 docs | Complete |

---

## Sign-Off Required

- [ ] User approves critical fixes (vigilance, TTL, integration tests)
- [ ] User accepts 2-day timeline
- [ ] User confirms P1 fixes can be post-v1 if needed
- [ ] Test coverage target: 25+ tests
- [ ] Performance target: <100ms average

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Vigilance integration complex | Medium | High | Start with simple source checking |
| Honcho API changes | Low | Medium | Abstract client behind interface |
| Performance regression | Low | Medium | Benchmark before/after each change |
| Config breaking changes | Low | Low | Validate early, fail fast |

---

## Next Steps After Sign-Off

1. Implement critical fixes (Phase 1)
2. Run full test suite
3. Verify performance benchmarks
4. Commit with `[verified]` prefix
5. Tag v0.1.0-rc1
6. Deploy to staging for validation

---

**Synthesis Complete.** 5 critical fixes required, 7 high priority. Total effort: 12 hours over 2 days.
