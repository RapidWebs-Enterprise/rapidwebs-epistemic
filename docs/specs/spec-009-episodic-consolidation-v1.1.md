---
name: episodic-consolidation-engine
description: Background synthesis engine that creates Episode → Summary → Insight hierarchy from raw conversation transcripts
status: proposed
created: 2026-09-21
updated: 2026-09-21
version: 1.1
author: Lucien (RapidWebs)
related-adrs: [ADR-008]
review-status: reviewed
---

# Spec v1.1: Episodic Consolidation Engine

## Review Summary

**Changes from v1.0:**
- Added configuration schema for consolidation depth
- Clarified async processing pipeline
- Added integration points with ToM Tier 3
- Added performance considerations (queue depth, LLM cost)

## Context

Honcho stores raw conclusions but doesn't synthesize them into higher-level patterns. Users must query individually; no automatic insight generation across sessions. This creates context window pressure and misses cross-session patterns.

**Problem:** No mechanism to distill raw transcripts into actionable insights.

**Solution:** Background consolidation engine that creates hierarchical memory: Episode → Summary → Insight.

## Requirements

### R1: Three-Tier Hierarchy
The system SHALL create and maintain:
- **Episode**: Raw message batch (preserved for audit)
- **Summary**: LLM-extracted key points (compact representation)
- **Insight**: Cross-episode pattern detection (actionable knowledge)

#### Scenario: Episode creation
- **GIVEN** session with 50 messages
- **WHEN** session ends
- **THEN** creates Episode record with timestamp and message IDs

#### Scenario: Summary generation
- **GIVEN** Episode with 50 messages
- **WHEN** consolidation worker processes
- **THEN** creates Summary with bullet points of key decisions

#### Scenario: Insight extraction
- **GIVEN** 10 Sessions with related summaries
- **WHEN** pattern detector runs
- **THEN** creates Insight: "User consistently asks about deployment on Mondays"

### R2: Async Background Processing
The system SHALL process consolidation asynchronously:
- Episode creation: Synchronous (on session end)
- Summary generation: Async worker (queue-based)
- Insight extraction: Periodic batch (daily)

#### Scenario: Non-blocking session end
- **GIVEN** session completes
- **WHEN** consolidation triggered
- **THEN** session returns immediately, processing continues in background

### R3: Configurable Depth
Users SHALL configure consolidation depth:
```yaml
episodic_consolidation:
  enabled: true
  summary_depth: "key_points"  # key_points | detailed | minimal
  insight_window: 7  # days
  max_insights_per_topic: 5
```

## Non-Requirements

- Does NOT replace raw transcript storage (episodes preserved)
- Does NOT require real-time processing (batch OK)
- Does NOT modify existing conclusion schema
- Does NOT persist insights across workspaces
- Does NOT require additional database dependencies

## Design Notes

### Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Session End   │────▶│   Episode Store │────▶│  Summary Worker │
│  (synchronous)  │     │  (append-only)  │     │  (async queue)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                      │
                                                      ▼
                                            ┌─────────────────┐
                                            │  Insight Engine │
                                            │  (daily batch)  │
                                            └─────────────────┘
                                                      │
                                                      ▼
                                            ┌─────────────────┐
                                            │   Insight Store │
                                            │ (cross-session) │
                                            └─────────────────┘
```

### Data Models
```python
@dataclass
class Episode:
    episode_id: str
    session_id: str
    user_id: str
    messages: list[dict]  # Raw transcript
    created_at: datetime
    status: str = "raw"  # raw | summarizing | summarized

@dataclass
class Summary:
    summary_id: str
    episode_id: str
    key_points: list[str]
    decisions: list[str]
    open_questions: list[str]
    created_at: datetime

@dataclass
class Insight:
    insight_id: str
    topic: str
    pattern: str
    confidence: float
    supporting_summaries: list[str]
    created_at: datetime
    expires_at: Optional[datetime] = None
```

### Integration with ToM
Insights SHALL feed into Theory of Mind Tier 3:
```python
# In Tier3Store.merge_session_model()
if insight.confidence > 0.7:
    model.insights.append(insight)
```

### Performance Considerations
| Operation | Latency | Notes |
|-----------|---------|-------|
| Episode creation | <1ms | Synchronous, append-only |
| Summary generation | ~2s | LLM call, async |
| Insight extraction | ~5s | Batch processing, daily |
| Queue depth monitoring | <10ms | Metric export |

## Open Questions

1. How to handle contradictory insights over time?
2. Should insights have TTL (time-to-live)?
3. How to surface insights to agents (tool call vs. context injection)?
4. What's the optimal batch size for insight extraction?

## References

- Spec: spec-009-episodic-consolidation.md
- Mem0 (arXiv:2504.19413): Hierarchical memory consolidation
- ECHO (arXiv:2608.21755): Immutable episodes with projections
- Honcho dreamer subsystem (existing async worker pattern)
