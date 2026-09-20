# Epistemic Vigilance Implementation Plan

**Date:** 2026-09-20  
**Status:** Ready for Implementation  
**Priority:** P0 (Critical Gap)

---

## Overview

Implement claim verification against available sources (Honcho KG, tool results, session context) to flag unverified statements in agent responses.

---

## Implementation Tasks

### Task 1: Claim Extraction (~1h)
```python
def _extract_claims(self, response: str) -> list[dict]:
    """Extract verifiable claims from text."""
    claims = []
    sentences = re.split(r'[.!?]+', response)
    
    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 20:
            continue
        
        # Check for factual indicators
        if any(marker in sent.lower() for marker in FACTUAL_MARKERS):
            claims.append({
                "text": sent[:200],
                "type": "factual",
                "confidence": 0.8
            })
    
    return claims
```

**Constants needed:**
- `FACTUAL_MARKERS = ["the", "is", "are", "was", "were", "has", "have", "according to", "studies show"]`
- `OPINION_MARKERS = ["i think", "i believe", "maybe", "possibly", "might", "could"]`

---

### Task 2: Source Verification (~2h)
```python
async def _verify_claim(self, claim: dict) -> dict:
    """Check claim against available sources."""
    result = {
        "claim": claim["text"],
        "status": "unverified",
        "sources_checked": [],
        "evidence": []
    }
    
    # 1. Check Honcho KG
    honcho_results = await self._query_honcho(claim["text"])
    if honcho_results:
        result["sources_checked"].append("honcho_kg")
        if honcho_results.get("confirmed"):
            result["status"] = "verified"
            result["evidence"].append(honcho_results["source"])
    
    # 2. Check recent tool results
    tool_results = self._check_tool_results(claim["text"])
    if tool_results:
        result["sources_checked"].append("tool_results")
        # Similar logic...
    
    # 3. Check session context
    context_results = self._check_session_context(claim["text"])
    if context_results:
        result["sources_checked"].append("session_context")
        # Similar logic...
    
    return result
```

---

### Task 3: Hook Integration (~1h)
```python
async def _post_llm_call_vigilance(self, **kwargs):
    """Run vigilance checks after LLM response."""
    response = kwargs.get("assistant_response", "")
    if not response:
        return None
    
    claims = self._extract_claims(response)
    if not claims:
        return None
    
    verified_count = 0
    unverified_claims = []
    
    for claim in claims:
        result = await self._verify_claim(claim)
        if result["status"] == "verified":
            verified_count += 1
        else:
            unverified_claims.append(result)
    
    if unverified_claims:
        warning = self._format_warning(unverified_claims)
        return {"context": warning}
    
    return None
```

---

### Task 4: Tests (~1h)
```python
class TestEpistemicVigilance:
    def test_claim_extraction(self):
        """Should extract factual claims."""
        response = "The Honcho API endpoint is /v3/peers/{id}/chat"
        claims = vigilance._extract_claims(response)
        assert len(claims) > 0
        assert claims[0]["type"] == "factual"
    
    def test_opinion_not_claim(self):
        """Should not flag opinions."""
        response = "I think this might be the best approach"
        claims = vigilance._extract_claims(response)
        assert len(claims) == 0
    
    def test_verification_with_honcho(self):
        """Should verify against Honcho KG."""
        # Mock Honcho response
        claim = {"text": "Honcho has KG tools", "type": "factual"}
        result = asyncio.run(vigilance._verify_claim(claim))
        # Assert based on mock
```

---

## Dependencies

- Honcho client wrapper (already exists in honcho_client.py)
- Session transcript access (from hook kwargs)
- Tool result history (from hook kwargs)

---

## Success Criteria

- [ ] Claims extracted correctly (precision > 80%)
- [ ] Honcho KG integration working
- [ ] Warning injection format correct
- [ ] No false positives on opinions
- [ ] Tests passing (8+ new tests)
- [ ] Performance < 500ms overhead

---

## Estimated Effort

- **Task 1:** 1 hour
- **Task 2:** 2 hours
- **Task 3:** 1 hour
- **Task 4:** 1 hour
- **Total:** 5 hours

---

## Integration with Existing Code

Add to `__init__.py`:
```python
class EpistemicVigilance:
    """Continuous monitoring for hallucinations and unverified claims."""
    
    def __init__(self, honcho_client=None):
        self.honcho = honcho_client
        self._tool_results = []
    
    # ... methods ...
```

Register in `register()`:
```python
vigilance = EpistemicVigilance(honcho_client=get_honcho_client())
ctx.register_hook("post_llm_call", vigilance.check_response)
```

---

**Ready to implement after v0.1.0 deployment validation.**
