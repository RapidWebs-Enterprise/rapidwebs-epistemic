# rapidwebs-epistemic — Epistemic Enhancement Layer

**Status:** Scaffolded (v0.1.0)  
**Author:** RapidWebs (Lucien)  
**License:** MIT

## Overview

The epistemic enhancement layer adds three capabilities to Hermes Agent:

1. **Epistemic Confidence Scoring** — Agents estimate their own certainty (0.0-1.0)
2. **Self-Model Persistence** — Agents learn from past mistakes across sessions
3. **Epistemic Vigilance** — Continuous monitoring for hallucinations and logical errors

Based on 2025 research in agent self-awareness (INWARD, KnowSelf, MetaCrit).

## Architecture

```
rapidwebs-epistemic/
├── __init__.py           # Plugin entry point + 3 core components
├── plugin.yaml           # Plugin metadata and hooks
├── hooks/                # Shell hook scripts
├── tests/                # Unit tests
│   └── test_epistemic.py
└── docs/
    ├── specs/            # Feature specifications
    ├── adrs/             # Architecture Decision Records
    ├── plans/            # Implementation plans
    ├── research/         # Research documents
    └── templates/        # Spec/ADR/Plan templates
```

## Components

### 1. ConfidenceEstimator
- Analyzes response patterns for uncertainty markers
- Weighs tool verification density
- Computes confidence score (0.0-1.0)
- Injects context when below threshold

### 2. SelfModel
- Persistent JSON storage of agent identity
- Tracks capabilities, limitations, past mistakes
- Extracts preferences from user interactions
- Loads at session start for continuity

### 3. EpistemicVigilance
- Extracts claims from responses
- Checks against available sources
- Flags unverified statements
- Integrates with post_llm_call hook

## Installation

```bash
# Plugin is in ~/.hermes/plugins/rapidwebs-epistemic/
# Add to config.yaml:

plugins:
  enabled:
    - rapidwebs-epistemic

# Configuration:
rapidwebs-epistemic:
  confidence_threshold: 0.7
  self_model_enabled: true
  vigilance_enabled: true
```

## Testing

```bash
cd ~/.hermes/plugins/rapidwebs-epistemic
python -m pytest tests/ -v
```

## Research Foundation

- **INWARD (2025)**: LLMs can access facts about themselves independent of training data
- **KnowSelf (ACL 2025)**: Agentic knowledgeable self-awareness improves planning
- **MetaCrit (2025)**: Multi-agent self-reflection improves truthfulness by 34%
- **Episodic Memory Position (2025)**: Temporal decay essential for long-term agents

## Status

- [x] Plugin scaffold created
- [x] Core components implemented (ConfidenceEstimator, SelfModel)
- [ ] EpistemicVigilance component complete
- [ ] Hook integration complete
- [ ] Tests passing
- [ ] Documentation complete

## Next Steps

1. Complete EpistemicVigilance implementation
2. Add shell hooks for pre_llm_call and post_llm_call
3. Run full test suite
4. Create ADRs for architectural decisions
5. Write implementation plan
6. Deploy and validate
