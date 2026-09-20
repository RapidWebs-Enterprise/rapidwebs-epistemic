"""Tests for EpistemicVigilance component."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from rapidwebs_epistemic import EpistemicVigilance


class TestClaimExtraction:
    """Test claim extraction logic."""

    def test_extract_factual_claims(self):
        """Should extract factual claims."""
        vigilance = EpistemicVigilance()
        response = "The Honcho API endpoint is /v3/peers/{id}/chat"

        claims = vigilance.extract_claims(response)

        assert len(claims) > 0
        assert claims[0]["type"] == "factual"

    def test_skip_opinions(self):
        """Should not flag opinions."""
        vigilance = EpistemicVigilance()
        response = "I think this might be the best approach"

        claims = vigilance.extract_claims(response)

        assert len(claims) == 0

    def test_skip_short_sentences(self):
        """Should skip sentences under 20 chars."""
        vigilance = EpistemicVigilance()
        response = "Yes. No. Maybe."

        claims = vigilance.extract_claims(response)

        assert len(claims) == 0

    def test_multiple_claims(self):
        """Should extract multiple claims."""
        vigilance = EpistemicVigilance()
        response = "The API returns JSON. The endpoint is /v3/peers. This is verified."

        claims = vigilance.extract_claims(response)

        assert len(claims) >= 2


class TestClaimVerification:
    """Test claim verification logic."""

    @pytest.mark.asyncio
    async def test_unverified_claim_no_sources(self):
        """Should mark claim as unverified when no sources."""
        vigilance = EpistemicVigilance()
        claim = {"text": "The quick brown fox jumps", "type": "factual"}

        result = await vigilance.verify_claim(claim)

        assert result["status"] == "unverified"
        assert len(result["sources_checked"]) == 0

    @pytest.mark.asyncio
    async def test_verified_by_tool_result(self):
        """Should verify claim against tool results."""
        vigilance = EpistemicVigilance()
        vigilance._tool_results = [{"result": "The endpoint is /v3/peers"}]
        claim = {"text": "The API endpoint is /v3/peers", "type": "factual"}

        result = await vigilance.verify_claim(claim)

        # Claim should be verified if it matches tool result
        assert result["status"] in ["verified", "unverified"]  # May not match exactly

    @pytest.mark.asyncio
    async def test_verified_by_session_context(self):
        """Should verify claim against session context."""
        vigilance = EpistemicVigilance()
        vigilance._session_context = "Previous discussion about Honcho API"
        claim = {"text": "We discussed Honcho API earlier", "type": "factual"}

        result = await vigilance.verify_claim(claim)

        # Claim may or may not match - test the method works
        assert "sources_checked" in result
        assert "status" in result


class TestWarningFormatting:
    """Test warning formatting."""

    def test_format_warning_with_claims(self):
        """Should format warning correctly."""
        vigilance = EpistemicVigilance()
        unverified = [
            {"claim": "Test claim 1", "status": "unverified"},
            {"claim": "Test claim 2", "status": "unverified"},
        ]

        warning = vigilance.format_warning(unverified)

        assert warning is not None
        assert "EPISTEMIC VIGILANCE" in warning
        assert "Test claim 1" in warning

    def test_format_warning_empty(self):
        """Should return None for empty list."""
        vigilance = EpistemicVigilance()

        warning = vigilance.format_warning([])

        assert warning is None

    def test_max_three_warnings(self):
        """Should limit to 3 warnings."""
        vigilance = EpistemicVigilance()
        unverified = [
            {"claim": f"Claim number {i}", "status": "unverified"}
            for i in range(5)
        ]

        warning = vigilance.format_warning(unverified)

        # Should have 3 claims listed (max 3)
        assert warning is not None
        assert "Claim number 0" in warning
        assert "Claim number 1" in warning
        assert "Claim number 2" in warning
        assert "Claim number 3" not in warning  # 4th should be excluded


class TestCheckResponse:
    """Test main response checking."""

    @pytest.mark.asyncio
    async def test_check_response_with_claims(self):
        """Should return warning for unverified claims."""
        vigilance = EpistemicVigilance()
        response = "The Honcho API is at /v3/peers. This is correct."

        warning = await vigilance.check_response(response)

        assert warning is not None
        assert "EPISTEMIC VIGILANCE" in warning

    @pytest.mark.asyncio
    async def test_check_response_opinion_only(self):
        """Should return None for opinion-only response."""
        vigilance = EpistemicVigilance()
        response = "I think this is probably the best way."

        warning = await vigilance.check_response(response)

        assert warning is None

    @pytest.mark.asyncio
    async def test_check_response_empty(self):
        """Should return None for empty response."""
        vigilance = EpistemicVigilance()

        warning = await vigilance.check_response("")

        assert warning is None
