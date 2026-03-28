"""
tests/test_health.py - Health Check Tests
==========================================
Smoke tests to verify the application starts correctly
and basic endpoints respond.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test that the health endpoint returns 200 with expected payload."""
    response = await client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "service" in data


@pytest.mark.asyncio
async def test_docs_available(client: AsyncClient):
    """Test that the OpenAPI docs endpoint is accessible."""
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_api_v1_repos_empty(client: AsyncClient):
    """Test that listing repos returns an empty list initially."""
    response = await client.get("/api/v1/repos/")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 0
    assert data["repositories"] == []
