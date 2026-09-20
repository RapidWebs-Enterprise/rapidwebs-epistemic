---
title: "ADR-002: Self-Model Storage Format"
description: "Decision to use JSON file with atomic writes vs. database backend"
category: architecture
tags:
  - epistemic
  - self-model
  - storage
---

# ADR-002: Self-Model Storage Format

**Status**: Accepted  
**Date**: 2026-09-20  
**Deciders**: Lucien (RapidWebs)  
**Consulted**: Steven Page  
**Informed**: Engineering team

## Context

The self-model needs persistent storage that survives session restarts and process crashes. Two approaches were considered:

**Option A: JSON File**
- Simple, human-readable
- Atomic writes via temp+rename
- No external dependencies

**Option B: SQLite Database**
- Structured queries
- Concurrent access safety
- Requires database management

## Decision

We will implement **Option A: JSON file storage**.

**Rationale:**
1. Self-model is small (<10KB typically)
2. Single-writer pattern (one agent session at a time)
3. Human-readable for debugging
4. No database maintenance overhead
5. Consistent with existing patterns (SESSION_STATE.md)

## Alternatives Considered

| Option | Description | Pros | Cons | Reason Rejected |
|--------|-------------|------|------|-----------------|
| **A** | JSON file | Simple, readable | Manual cleanup | Chosen for simplicity |
| **B** | SQLite | Structured queries | Overhead for small data | Unnecessary complexity |
| **C** | Honcho peer | Cross-session sharing | Dependency coupling | Self-model is agent-specific |

## Consequences

### Positive
- Zero external dependencies
- Easy to inspect and edit manually
- Atomic writes prevent corruption
- Human-readable for debugging

### Negative
- No concurrent access safety (acceptable — single agent)
- Manual cleanup needed for old mistakes
- No query capabilities

### Neutral/Follow-ups
- Consider SQLite if model grows >50KB
- Could sync to Honcho for cross-agent sharing later

## Implementation Notes

- Location: `~/.hermes/epistemic/self_model.json`
- Write pattern: temp file → rename (atomic on POSIX)
- Prune mistakes older than 90 days
- Keep max 50 mistakes

## References

- JSON atomic write pattern used in graph.py, branch.py
- SESSION_STATE.md precedent in rapidwebs-sessions
