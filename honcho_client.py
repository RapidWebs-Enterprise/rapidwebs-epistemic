"""Honcho client for epistemic vigilance."""

import logging
from typing import Any, Optional

logger = logging.getLogger("rapidwebs-epistemic")


class HonchoClient:
    """Lightweight Honcho client for entity verification."""

    def __init__(self, base_url: str = "http://100.79.58.118:8000"):
        self.base_url = base_url.rstrip("/")
        self._session = None

    async def search_entities(self, query: str, limit: int = 5) -> list[dict]:
        """Search entities by query."""
        try:
            import aiohttp
            url = f"{self.base_url}/v3/workspaces/hermes/kg/entities"
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params={"q": query, "limit": limit},
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("entities", [])
        except Exception as e:
            logger.debug("Honcho entity search failed: %s", e)
        return []

    async def verify_claim(self, claim: str) -> dict:
        """Verify a claim against Honcho KG."""
        result = {
            "claim": claim,
            "status": "unverified",
            "sources_checked": ["honcho_kg"],
            "evidence": [],
        }

        entities = await self.search_entities(claim[:100], limit=3)
        for ent in entities:
            if ent.get("name", "").lower() in claim.lower():
                result["status"] = "verified"
                result["evidence"].append(f"Honcho: {ent.get('name')}")

        return result
