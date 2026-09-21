# Forward Audit: Causal Reasoning Graph

**Date:** 2026-09-21  
**Spec:** spec-007-causal-reasoning-graph-v1.1.md  
**ADR:** adr-006-causal-reasoning-graph-v1.1.md  
**Auditor:** Lucien (Inline)  
**Mode:** HIGH

---

## Spec Compliance Check

### R1: Causal Edge Type
**Requirement:** Add `KGCausalRelationship` with confidence, evidence, inferred flag, temporal validity

**Verification:**
```python
# Spec defines:
class KGCausalRelationship(KGRelationship):
    cause_confidence: float = Field(ge=0.0, le=1.0)
    evidence_text: Optional[str] = None
    inferred: bool = True
    valid_from: datetime
    valid_to: Optional[datetime] = None
```

**Status:** ✅ COMPLETE — All required fields specified with types and constraints

---

### R2: Causal Query Endpoints
**Requirement:** Expose GET and POST endpoints for traversal

**Verification:**
```
GET /v3/workspaces/{w}/kg/causal/{entity}
  ?direction=outgoing|incoming|both
  ?max_depth=3
  ?include_provenance=true
  
POST /v3/workspaces/{w}/kg/causal/traverse
  {
    "start_entity": "...",
    "query_type": "why|what_happened",
    "max_depth": 3
  }
```

**Status:** ✅ COMPLETE — Both endpoints defined with parameters

---

### R3: Integration with Existing Components
**Requirement:** Wire into temporal decay, auto-extraction, epistemic vigilance, context-dump

**Verification:**
- Temporal decay: "Causal edges expire like other edges" ✅
- Auto-extraction: "LLM identifies causal language patterns" ✅
- Epistemic vigilance: "Causal claims flagged for verification" ✅
- Context-dump: "Include causal chains in dumps" ✅

**Status:** ✅ COMPLETE — All integration points specified

---

## Implementation Feasibility

| Component | Complexity | Risk | Mitigation |
|-----------|------------|------|------------|
| Schema migration | Medium | Low | JSONB extension avoids migration |
| Extraction prompt | Medium | Medium | Build on existing auto-extraction |
| Query endpoint | Low | Low | Follow existing KG query patterns |
| BFS traversal | Low | Low | Standard graph algorithm |

**Overall Risk:** LOW — Leverages existing KG infrastructure

---

## Requirements Coverage

| Req ID | Description | Status | Testable |
|--------|-------------|--------|----------|
| R1 | Causal edge type | ✅ Complete | Yes |
| R2 | Query endpoints | ✅ Complete | Yes |
| R3 | Integrations | ✅ Complete | Yes |

**Coverage:** 100%

---

## Missing Elements

| Gap | Severity | Recommendation |
|-----|----------|----------------|
| No error handling spec | 🟡 Medium | Add 404/400/500 response codes |
| No pagination for deep traversals | 🟡 Medium | Add offset/limit params |
| No rate limiting specified | 🟢 Low | Add to API security section |

---

## Testability Assessment

### Unit Tests Required
1. `test_causal_edge_creation` — Verify schema
2. `test_bidirectional_traversal` — Verify both directions
3. `test_max_depth_enforcement` — Verify depth limit
4. `test_temporal_validity_filtering` — Verify valid_to filtering
5. `test_extraction_patterns` — Verify causal language detection

**Estimated tests:** 15-20

### Integration Tests Required
1. `test_causal_query_endpoint` — E2E endpoint test
2. `test_traverse_endpoint` — E2E traverse test
3. `test_integration_with_temporal_decay` — Verify decay applies
4. `test_integration_with_vigilance` — Verify flags unverified claims

**Estimated tests:** 8-10

---

## API Contract Completeness

| Aspect | Status | Notes |
|--------|--------|-------|
| Request format | ✅ Complete | JSON body defined |
| Response format | ✅ Complete | Includes confidence, provenance |
| Error responses | 🟡 Partial | Need to specify 404/400/500 |
| Authentication | ✅ Implied | Uses existing KG auth |
| Rate limiting | 🟢 Missing | Add to security section |

---

## Performance Considerations

| Operation | Complexity | Budget |
|-----------|------------|--------|
| Single entity query | O(degree) | <50ms |
| Deep traversal (depth=5) | O(b^d) | <500ms |
| Batch extraction | O(n) | Async, <1s per episode |

**Risk:** Deep traversals could be expensive. Consider:
- Enforce max_depth=5 hard limit
- Add timeout protection (500ms)
- Cache traversal results for repeated queries

---

## Open Questions Resolution

| Question | Answer | Status |
|----------|--------|--------|
| Schema migration approach | JSONB extension preferred | ✅ Resolved |
| Conflict handling | Latest causal claim wins | ✅ Resolved in ADR |
| Cross-workspace persistence | Not supported | ✅ Explicitly excluded |

---

## Verification Commands

```bash
# After implementation, verify with:
curl -X GET "http://localhost:8000/v3/workspaces/{w}/kg/causal/{entity}?direction=both&max_depth=3"
curl -X POST "http://localhost:8000/v3/workspaces/{w}/kg/causal/traverse" \
  -d '{"start_entity": "database_full", "query_type": "why", "max_depth": 3}'
```

---

## Overall Verdict

| Category | Status |
|----------|--------|
| Spec completeness | ✅ 95% (minor gaps) |
| Implementation feasibility | ✅ High |
| Test coverage plan | ✅ Complete |
| Performance bounds | ✅ Defined |
| Security considerations | 🟡 Needs addition |

**Recommendation:** PROCEED with implementation. Address error handling and rate limiting before coding.

---

**Audit Complete.** Causal Reasoning Graph spec is production-ready with minor additions needed.
