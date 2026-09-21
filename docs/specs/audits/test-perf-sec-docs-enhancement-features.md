# Test/Performance/Security Documentation: Honcho Enhancement Features

**Date:** 2026-09-21  
**Features:** Causal Graph, Confidence Retrieval, Episodic Consolidation  
**Auditor:** Lucien (Inline)  
**Mode:** HIGH

---

## Test Coverage Plan

### Causal Reasoning Graph

| Test Category | Tests | Coverage Target |
|---------------|-------|-----------------|
| Unit: Schema | 5 | 100% |
| Unit: Extraction | 8 | 100% |
| Unit: Traversal | 10 | 100% |
| Unit: Validation | 5 | 100% |
| Integration: API | 8 | 100% |
| Integration: DB | 5 | 100% |
| **Total** | **41** | **100%** |

**Key Test Scenarios:**
```python
def test_bidirectional_traversal():
    """Verify cause→effect and effect←cause both work."""
    
def test_max_depth_enforcement():
    """Verify depth=5 hard limit applied."""
    
def test_cycle_detection():
    """Verify A→B→C→A doesn't infinite loop."""
    
def test_temporal_validity_filtering():
    """Verify expired causal links excluded."""
```

---

### Confidence-Gated Retrieval

| Test Category | Tests | Coverage Target |
|---------------|-------|-----------------|
| Unit: Scoring | 12 | 100% |
| Unit: Filtering | 8 | 100% |
| Unit: Provenance | 5 | 100% |
| Integration: API | 6 | 100% |
| Integration: Plugin | 4 | 100% |
| **Total** | **35** | **100%** |

**Key Test Scenarios:**
```python
def test_multi_signal_scoring():
    """Verify weighted combination correct."""
    
def test_min_confidence_filtering():
    """Verify low-confidence conclusions excluded."""
    
def test_provenance_inclusion():
    """Verify sources returned when requested."""
    
def test_backward_compatibility():
    """Verify old queries still work without new params."""
```

---

### Episodic Consolidation

| Test Category | Tests | Coverage Target |
|---------------|-------|-----------------|
| Unit: Episode | 6 | 100% |
| Unit: Summary | 8 | 100% |
| Unit: Insight | 10 | 100% |
| Unit: Queue | 6 | 100% |
| Integration: Worker | 8 | 100% |
| Integration: ToM | 4 | 100% |
| **Total** | **42** | **100%** |

**Key Test Scenarios:**
```python
def test_async_processing():
    """Verify session end doesn't block."""
    
def test_queue_overflow():
    """Verify oldest dropped when full."""
    
def test_llm_failure_recovery():
    """Verify retry on LLM error."""
    
def test_insight_pattern_matching():
    """Verify semantic similarity works."""
```

---

## Performance Benchmarks

### Target Metrics

| Operation | Target | Acceptable | Critical |
|-----------|--------|------------|----------|
| Causal query (depth=3) | <100ms | <200ms | <500ms |
| Confidence score | <5ms | <10ms | <50ms |
| Episode creation | <1ms | <5ms | <100ms |
| Summary generation | <2s | <5s | <10s |
| Insight extraction | <5s | <10s | <30s |

### Benchmark Tests

```python
import pytest
import asyncio

@pytest.mark.performance
async def test_causal_query_latency():
    """Causal query must complete under 100ms."""
    start = time.perf_counter()
    result = await traverse_causal("entity", "both", 3)
    elapsed = time.perf_counter() - start
    assert elapsed < 0.1, f"Query took {elapsed:.3f}s"

@pytest.mark.performance
async def test_confidence_scoring_latency():
    """Confidence scoring must complete under 5ms."""
    start = time.perf_counter()
    score = calculate_confidence(conclusion)
    elapsed = time.perf_counter() - start
    assert elapsed < 0.005, f"Scoring took {elapsed:.3f}s"
```

---

## Security Considerations

### Threat Model

| Threat | Vector | Mitigation | Status |
|--------|--------|------------|--------|
| SQL Injection | Entity IDs | Parameterized queries | ✅ Specified |
| Path Traversal | Workspace IDs | Input validation | ✅ Specified |
| DoS | Deep traversal | Max depth=5 | ✅ Specified |
| DoS | Queue overflow | Queue limits | ✅ Specified |
| Prompt Injection | LLM calls | Input sanitization | ✅ Specified |
| Data Leak | Provenance | Sanitization | ✅ Specified |

### Security Tests

```python
def test_sql_injection_prevention():
    """Verify SQL injection attempts fail."""
    entity = "'; DROP TABLE kg_entities;--"
    with pytest.raises(ValueError):
        await traverse_causal(entity, "both", 3)

def test_path_traversal_prevention():
    """Verify path traversal blocked."""
    workspace = "../../etc/passwd"
    with pytest.raises(HTTPException):
        await get_causal(workspace, "entity")

def test_max_depth_enforcement():
    """Verify depth limit enforced."""
    result = await traverse_causal("entity", "both", 100)
    assert max_depth_used <= 5
```

---

## Risk Assessment

| Feature | Risk Level | Mitigation |
|---------|------------|------------|
| Causal Graph | 🟡 Medium | Cycle detection, depth limits |
| Confidence Retrieval | 🟢 Low | Input validation, caching |
| Episodic Consolidation | 🟠 High | Queue limits, retry logic |

---

## CI/CD Integration

### Required Pipeline Steps

```yaml
test:
  steps:
    - run: pytest tests/test_causal_graph.py -v
    - run: pytest tests/test_confidence.py -v
    - run: pytest tests/test_consolidation.py -v
    - run: pytest tests/performance/ -v
    - run: pytest tests/security/ -v
    - run: ruff check src/
    - run: basedpyright src/
```

### Coverage Requirements

| Metric | Target |
|--------|--------|
| Unit test coverage | ≥90% |
| Integration test coverage | ≥80% |
| Performance test pass rate | 100% |
| Security test pass rate | 100% |

---

## Documentation Requirements

### API Documentation
- [ ] OpenAPI spec updated
- [ ] Request/response examples
- [ ] Error code documentation
- [ ] Rate limiting docs

### Developer Documentation
- [ ] Architecture diagram
- [ ] Data flow diagrams
- [ ] Migration guide
- [ ] Troubleshooting guide

### User Documentation
- [ ] Feature overview
- [ ] Usage examples
- [ ] Configuration guide
- [ ] FAQ

---

## Sign-off Checklist

- [ ] All unit tests written
- [ ] All integration tests written
- [ ] Performance benchmarks passing
- [ ] Security tests passing
- [ ] Documentation complete
- [ ] Code review completed
- [ ] Stakeholder approval obtained

---

**Test/Perf/Sec Docs Complete.** All documentation requirements specified.
