# rapidwebs-epistemic — Epistemic Enhancement Layer

**Status:** ✅ Production Ready (v0.1.0)  
**Author:** RapidWebs (Lucien)  
**License:** MIT  
**Repository:** https://github.com/RapidWebs-Enterprise/rapidwebs-epistemic

---

## Overview

The epistemic enhancement layer adds four capabilities to Hermes Agent that no other plugin provides:

1. **Epistemic Confidence Scoring** — Agents estimate their own certainty (0.0-1.0)
2. **Self-Model Persistence** — Agents learn from past mistakes across sessions
3. **Epistemic Vigilance** — Continuous monitoring for hallucinations and unverified claims
4. **Theory of Mind Integration** — Three-tier user mental state modeling

Based on 2025 research in agent self-awareness (INWARD, KnowSelf, MetaCrit).

---

## Architecture

```
rapidwebs-epistemic/
├── __init__.py              # Plugin entry point + core components
├── honcho_client.py         # Lightweight Honcho KG client
├── src/
│   └── user_model.py        # Theory of Mind three-tier model
├── plugin.yaml              # Plugin metadata and hooks
├── hooks/                   # Shell hook scripts (optional)
├── tests/                   # Unit tests (58 passing)
│   ├── test_epistemic.py    # Confidence + SelfModel tests
│   ├── test_integration.py  # Hook integration tests
│   ├── test_vigilance.py    # Claim verification tests
│   └── test_user_model.py   # ToM tier tests
└── docs/
    ├── specs/               # 6 feature specifications
    ├── adrs/                # 5 architecture decision records
    ├── plans/               # Implementation plans
    ├── research/            # Research summaries
    ├── audits/              # Forward/reverse audit reports
    └── reports/             # Synthesis and deployment guides
```

---

## Components

### 1. ConfidenceEstimator
- Analyzes response patterns for uncertainty markers
- Weighs tool verification density
- Computes confidence score (0.0-1.0)
- Injects context when below threshold (default: 0.7)
- **Config:** `_CONFIDENCE_THRESHOLD = 0.7`

### 2. SelfModel
- Persistent JSON storage at `~/.hermes/epistemic/self_model.json`
- Tracks capabilities, limitations, past mistakes
- Extracts preferences from user interactions
- Loads at session start for continuity
- TTL pruning: 90-day expiry on old mistakes

### 3. EpistemicVigilance
- Extracts factual claims from responses
- Checks against Honcho KG, tool results, session context
- Flags unverified statements with warnings
- Integrates with `post_llm_call` hook
- Max 3 warnings per response

### 4. Theory of Mind (Three-Tier Model)
**Tier 1:** Raw session transcripts (`tier1/sessions/{user_id}/`)
- Append-only, 30-day TTL
- Stores full conversation history

**Tier 2:** Per-session models (`tier2/session_models/{user_id}/`)
- Extracted preferences, goals, emotional state
- 90-day retention

**Tier 3:** Aggregated model (`tier3/overall_model/{user_id}/model.json`)
- Cross-session patterns
- Goal tracking, preference consolidation
- Prediction engine for next requests

---

## Installation

Plugin is installed at `~/.hermes/plugins/rapidwebs_epistemic/`.

### Enable in config.yaml
```yaml
plugins:
  enabled:
    - rapidwebs-epistemic
```

### Configuration (optional)
```yaml
rapidwebs-epistemic:
  confidence_threshold: 0.7
  self_model_enabled: true
  vigilance_enabled: true
  temporal_decay:
    enabled: true
    half_life_days: 7
    min_weight: 0.01
```

---

## Testing

```bash
cd ~/.hermes/plugins/rapidwebs_epistemic
python -m pytest tests/ -v
```

**Current Status:**
```
58 passed in 0.38s
├── test_epistemic.py: 17 tests (confidence + self-model)
├── test_integration.py: 13 tests (hook integration)
├── test_vigilance.py: 13 tests (claim verification)
└── test_user_model.py: 17 tests (ToM components)
```

---

## Hook Integration

| Hook | Handler | Purpose |
|------|---------|---------|
| `pre_llm_call` | Confidence injection | Warn when confidence < 0.7 |
| `on_session_start` | Self-model + ToM context | Load past lessons and user preferences |
| `on_session_end` | Self-model + ToM update | Save mistakes, extract preferences |
| `post_llm_call` | Vigilance checks | Flag unverified claims |

---

## Research Foundation

- **INWARD (2025):** LLMs can access facts about themselves independent of training data
- **KnowSelf (ACL 2025):** Agentic knowledgeable self-awareness improves planning
- **MetaCrit (2025):** Multi-agent self-reflection improves truthfulness by 34%
- **Episodic Memory Position (2025):** Temporal decay essential for long-term agents
- **ToM-SWE (2025):** Dedicated Theory of Mind agent achieves 59.7% vs 18.1% success

---

## Files Summary

| Metric | Count |
|--------|-------|
| Source files | 3 (.py) |
| Test files | 4 (.py) |
| Documentation | 38 (.md) |
| Total commits | 10 |
| Tests passing | 58 |
| Lines of code | ~2,500 |

---

## Next Steps (Future)

1. **Enhanced extraction heuristics** — LLM-based preference detection
2. **Multi-user support** — Current single-user model sufficient for now
3. **Telemetry/metrics** — Track extraction accuracy over time
4. **Advanced predictions** — Time-based forecasting of user needs

---

## Deployment Status

| Component | Location | Status |
|-----------|----------|--------|
| Epistemic Plugin | Workstation | ✅ Loaded |
| Honcho Server | infra:8000 | ✅ Running |
| Temporal Decay | Honcho | ✅ Active (7-day half-life) |
| Config | ~/.hermes/honcho.json | ✅ Updated |

---

**Last Updated:** 2026-09-21  
**Version:** v0.1.0
