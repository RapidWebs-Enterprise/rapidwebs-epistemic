---
title: "Implementation Plan: Theory of Mind v1.0"
description: "Structured plan for user mental state modeling"
category: planning
tags:
  - implementation
  - theory-of-mind
  - epistemic
---

# Implementation Plan: Theory of Mind v1.0

## Overview

- **Feature:** Theory of Mind Integration
- **Objective:** Three-tier user mental state modeling with inference engine
- **Success Criteria:** 20+ tests passing, Tier 1-3 persistence working
- **Timeline:** 2026-09-21 to 2026-09-22
- **Owner:** Lucien (RapidWebs)
- **Status:** Not started

## Scope

### In Scope
- `UserMentalState` dataclass and persistence
- Tier 1: Session transcript storage
- Tier 2: Per-session model extraction
- Tier 3: Cross-session aggregation
- Preference extraction (style, format, tools)
- Emotional state detection
- Basic prediction engine

### Out of Scope
- Multi-user support (single user per account)
- Real-time inference (batch per session)
- Biometric data storage
- Group/fleet modeling

## Phases

### Phase 1: Core Data Model
**Duration:** 2 hours
**Start:** 2026-09-21
**Target:** 2026-09-21

- [ ] 1.1 Create `user_model.py` with `UserMentalState` dataclass
- [ ] 1.2 Implement Tier 1 storage (session transcripts)
- [ ] 1.3 Implement Tier 2 storage (per-session models)
- [ ] 1.4 Implement Tier 3 storage (aggregated model)
- [ ] 1.5 Write unit tests for data classes

**Deliverable:** Data model with persistence  
**Risk:** Low — straightforward file I/O

### Phase 2: Extraction Logic
**Duration:** 3 hours
**Start:** 2026-09-21
**Target:** 2026-09-21

- [ ] 2.1 Implement preference extraction (style, format, tools)
- [ ] 2.2 Implement emotional state detection
- [ ] 2.3 Implement goal inference from task completion
- [ ] 2.4 Add extraction tests

**Deliverable:** Working extraction pipeline  
**Risk:** Medium — heuristic-based, may need tuning

### Phase 3: Aggregation & Prediction
**Duration:** 2 hours
**Start:** 2026-09-21
**Target:** 2026-09-21

- [ ] 3.1 Implement Tier 3 aggregation (merge patterns)
- [ ] 3.2 Add prediction engine (next request, roadblocks)
- [ ] 3.3 Wire into plugin hooks
- [ ] 3.4 Add integration tests

**Deliverable:** Complete ToM system  
**Risk:** Medium — aggregation logic complex

### Phase 4: Testing & Documentation
**Duration:** 1 hour
**Start:** 2026-09-21
**Target:** 2026-09-21

- [ ] 4.1 Run full test suite (target: 20+ tests)
- [ ] 4.2 Update README with usage examples
- [ ] 4.3 Commit and push

**Deliverable:** Production-ready feature  
**Risk:** Low

## Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| Epistemic plugin foundation | Lucien | ✅ Complete |
| Honcho client | Lucien | ✅ Complete |
| Test infrastructure | Lucien | ✅ Ready |

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Heuristic extraction inaccurate | Medium | Medium | Start simple, tune iteratively |
| Tier coordination complexity | Medium | Low | Clear separation, well-defined APIs |
| Performance overhead | Low | Low | Batch updates, lazy loading |

## Success Metrics

| Metric | Target |
|--------|--------|
| Test coverage | >80% |
| Extraction accuracy | >70% (manual validation) |
| Prediction precision | >60% (session testing) |
| Storage growth | <1MB per 100 sessions |

## Files to Modify/Create

1. `src/user_model.py` — NEW: Core data model
2. `src/tier1_session_store.py` — NEW: Raw transcripts
3. `src/tier2_session_model.py` — NEW: Per-session analysis
4. `src/tier3_aggregator.py` — NEW: Cross-session aggregation
5. `src/prediction_engine.py` — NEW: Next request prediction
6. `tests/test_user_model.py` — NEW: Data model tests
7. `tests/test_tom_integration.py` — NEW: Integration tests
8. `README.md` — MODIFY: Add ToM documentation

## References

- Spec: docs/specs/spec-006-theory-of-mind.md
- ADR: docs/adrs/adr-005-theory-of-mind-model.md
- Research: ToM-SWE (2025), M3 (2025)
