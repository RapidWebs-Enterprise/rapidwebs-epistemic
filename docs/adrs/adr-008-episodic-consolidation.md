---
title: "ADR-008: Episodic Consolidation Engine"
description: "Decision to add background synthesis engine for Episode → Summary → Insight hierarchy"
category: architecture
tags:
  - honcho
  - memory
  - consolidation
  - async
---

# ADR-008: Episodic Consolidation Engine

**Status**: Proposed  
**Date**: 2026-09-21  
**Deciders**: Lucien (RapidWebs)  
**Consulted**: Steven Page  
**Informed**: Engineering team

## Context

Honcho stores raw conclusions but doesn't synthesize them into higher-level patterns. Users must query individually; no automatic insight generation across sessions. This creates context window pressure and misses cross-session patterns.

**Current state:** Messages → Conclusions (flat structure). No summarization or pattern detection.

**Problem:** Agents lack cross-session context and pattern recognition.

## Decision

We will implement a three-tier consolidation engine:
1. **Episode**: Raw message batch (append-only, preserved)
2. **Summary**: LLM-extracted key points (compact representation)
3. **Insight**: Cross-episode pattern detection (actionable knowledge)

Processing is asynchronous:
- Episode creation: Synchronous (on session end)
- Summary generation: Async worker (queue-based)
- Insight extraction: Periodic batch (daily)

**Decision:** Add consolidation engine as background worker, integrating with existing dreamer subsystem pattern.

## Alternatives Considered

| Option | Description | Pros | Cons | Reason Rejected |
|--------|-------------|------|------|-----------------|
| **A** | Async background processing (chosen) | Non-blocking, scalable | Latency for insights | Chosen for UX |
| **B** | Synchronous consolidation | Immediate results | Blocks session end | Rejected for latency |
| **C** | Real-time streaming | Always current | Complex, expensive | Rejected for cost |

## Consequences

### Positive
- Reduces context window pressure (summaries vs raw)
- Enables pattern detection across sessions
- Supports ToM integration (Tier 3 insights)
- Aligns with Mem0 hierarchical memory

### Negative
- Additional async worker to maintain
- LLM calls for summarization (cost)
- Storage for summaries and insights

### Neutral/Follow-ups
- Monitor worker queue depth
- Tune summarization frequency
- Evaluate insight TTL (expiration)

## Implementation Notes

1. Add `Episode`, `Summary`, `Insight` models to `src/models/`
2. Create `src/workers/consolidation.py` async worker
3. Add queue integration (Redis or in-memory)
4. Expose `/episodes`, `/summaries`, `/insights` API endpoints
5. Wire into ToM Tier 3 store

## References

- Spec: spec-009-episodic-consolidation.md
- Mem0 (arXiv:2504.19413): Hierarchical memory consolidation
- ECHO (arXiv:2608.21755): Immutable episodes with projections
- Honcho dreamer subsystem (existing async pattern)
