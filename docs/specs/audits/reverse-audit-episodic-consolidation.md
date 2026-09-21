# Reverse Audit: Episodic Consolidation Engine

**Date:** 2026-09-21  
**Spec:** spec-009-episodic-consolidation-v1.1.md  
**Auditor:** Lucien (Inline)  
**Mode:** HIGH

---

## Critical Gaps (Must Fix)

### 1. No Failure Recovery for LLM Calls 🔴
**Issue:** What if LLM summarization fails?

**Current spec:** No error handling mentioned

**Impact:** Episodes stuck in "summarizing" state forever

**Fix:** Add retry logic:
```python
async def generate_summary(episode: Episode) -> Summary:
    for attempt in range(3):
        try:
            return await llm.summarize(episode.messages)
        except LLMError:
            if attempt == 2:
                return Summary(fallback="Summarization failed")
            await asyncio.sleep(2 ** attempt)
```

---

### 2. No Queue Overflow Handling 🔴
**Issue:** What if episodes pile up faster than processing?

**Current spec:** No queue depth limits

**Impact:** Memory exhaustion, delayed processing

**Fix:** Add backpressure:
```python
if queue.size > MAX_QUEUE_DEPTH:
    # Drop oldest episodes or block ingestion
    await queue.enqueue_with_backpressure(episode)
```

---

## High Priority Gaps

### 3. No Insight Expiration Logic 🟠
**Issue:** Old insights become stale but never expire

**Current spec:** Has `expires_at` field but no cleanup

**Fix:** Add TTL enforcement:
```python
async def purge_expired_insights():
    await db.execute(
        "DELETE FROM insights WHERE expires_at < NOW()"
    )
```

### 4. No Contradiction Detection 🟠
**Issue:** Conflicting insights not resolved

**Example:**
- Insight 1: "User prefers concise responses" (session 1)
- Insight 2: "User wants detailed explanations" (session 5)

**Fix:** Add contradiction resolution:
```python
def resolve_insight_conflicts(insights: list[Insight]) -> list[Insight]:
    """Latest high-confidence insight wins."""
    return sorted(insights, key=lambda i: (i.confidence, i.created_at), reverse=True)[:1]
```

---

## Medium Priority Gaps

### 5. No LLM Prompt Specifications 🟡
**Issue:** How does summarization work? What prompt?

**Fix:** Add prompt templates:
```python
SUMMARY_PROMPT = """
Extract key points from this conversation:
{messages}

Return:
- key_points: list of important facts
- decisions: list of decisions made
- open_questions: list of unresolved issues
"""
```

### 6. No Processing Order Guarantees 🟡
**Issue:** What if summary for episode 5 processed before episode 1?

**Fix:** Add ordering:
```python
# Process in chronological order
episodes = await db.query("SELECT * FROM episodes ORDER BY created_at")
```

---

## Low Priority Gaps

### 7. No Monitoring/Metrics 🟢
**Issue:** Can't track processing health

**Fix:** Add metrics:
- Queue depth
- Processing latency
- Success/failure rates
- Insight generation rate

### 8. No User Control Over Consolidation 🟢
**Issue:** Users can't disable or adjust consolidation

**Fix:** Add per-user config:
```yaml
users:
  steven:
    episodic_consolidation:
      enabled: false  # Disable for this user
```

---

## Completeness Checklist

| Requirement | Status |
|-------------|--------|
| Data models | ✅ Complete |
| API endpoints | ✅ Complete |
| Async processing | ✅ Complete |
| Failure recovery | ❌ Missing |
| Queue management | ❌ Missing |
| LLM prompts | 🟡 Partial |
| Conflict resolution | ❌ Missing |
| Monitoring | 🟢 Low priority |

**Completion:** 65%

---

## Recommended Actions

1. **Immediate (P0):** Add failure recovery for LLM calls
2. **Immediate (P0):** Add queue overflow handling
3. **This Sprint (P1):** Implement insight expiration
4. **This Sprint (P1):** Add contradiction detection
5. **Next Sprint (P2):** Define LLM prompts
6. **Future (P3):** Monitoring and metrics

---

**Audit Complete.** Episodic Consolidation needs significant error handling before implementation.
