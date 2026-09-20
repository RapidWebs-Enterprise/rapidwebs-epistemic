---
name: epistemic-vigilance
description: Continuous monitoring system that detects hallucinations and flags unverified claims in agent responses
status: proposed
created: 2026-09-20
author: Lucien (RapidWebs)
related-adrs: [ADR-003]
---

# Spec: Epistemic Vigilance

## Context

Agents frequently generate plausible-sounding but incorrect information. Current systems have no mechanism to verify claims or flag uncertainty. Research shows hallucination detection can achieve 70%+ accuracy with proper frameworks (HalMit, FACTCHECKMATE).

**Problem:** No real-time monitoring for hallucinations or unverified claims.

**Solution:** Post-generation verification with claim extraction and source checking.

## Requirements

### R1: Claim Extraction
The system SHALL extract verifiable claims from agent responses using:
- Factual statements (declarative sentences)
- Specific names, dates, numbers
- Technical assertions requiring verification

#### Scenario: Response with claims
- **GIVEN** response contains "The Honcho API endpoint is /v3/peers/{id}/chat"
- **WHEN** post_llm_call hook executes
- **THEN** claim is extracted with text and position

#### Scenario: Opinion statement
- **GIVEN** response contains "I think this approach is best"
- **WHEN** post_llm_call hook executes
- **THEN** claim is marked as opinion, not factual

### R2: Source Verification
The system SHALL check claims against available sources:
1. Honcho KG (entities, relationships)
2. Recent tool results (file contents, command outputs)
3. Prior session context (SESSION_STATE.md)

#### Scenario: Claim verifiable via Honcho
- **GIVEN** claim references entity in Honcho KG
- **WHEN** verification executes
- **THEN** claim status = "verified" with source reference

#### Scenario: Claim unverifiable
- **GIVEN** claim has no source in available data
- **WHEN** verification executes
- **THEN** claim status = "unverified" flagged for review

### R3: Verification Results Injection
When unverified claims are detected, system SHALL:
1. Generate warning context
2. Inject into user message before response
3. Include claim text and verification status

#### Scenario: Multiple unverified claims
- **GIVEN** response contains 3 unverified claims
- **WHEN** post_llm_call hook completes
- **THEN** context includes list of all unverified claims

#### Scenario: All claims verified
- **GIVEN** all claims have supporting sources
- **WHEN** post_llm_call hook completes
- **THEN** no context injection occurs

### R4: Configuration
The system SHALL support:
- `vigilance_enabled`: Master toggle (default: true)
- `verification_sources`: List of sources to check
- `strict_mode`: Require verification for all factual claims

## Non-Requirements

- Does NOT require ground truth labels
- Does NOT block response delivery (informational only)
- Does NOT modify original response

## Design Notes

### Architecture
```
post_llm_call hook
    ↓
Extract claims from response
    ↓
For each claim:
  ├── Check Honcho KG
  ├── Check tool results
  └── Check session context
    ↓
Classify: verified / unverified / opinion
    ↓
If unverified count > 0:
  ├── Generate warning context
  └── Inject into user message
```

### Claim Detection heuristics
- Sentence starts with "The", "It is", "X is Y"
- Contains specific technical terms
- Makes causal assertions
- Excludes hedging language ("might", "could")

### Performance Considerations
- Verification runs async (non-blocking)
- Timeout per claim: 500ms
- Max claims to verify: 10 per response

## Open Questions

- How to balance verification overhead with response latency?
- Should we implement confidence-weighted verification?
- How to handle partial verification (some claims verified, some not)?

## References

- HalMit (arXiv:2507.15903): Black-box hallucination watchdog
- FACTCHECKMATE (EMNLP 2025): Preemptive hallucination detection
- HADEMIF (ICLR 2025): Dual-space hallucination detection
- InEx (AAAI 2025): Multi-agent collaboration for verification
