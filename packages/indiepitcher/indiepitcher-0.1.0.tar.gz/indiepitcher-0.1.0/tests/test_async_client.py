"""Tests for IndiePitcher async client."""

import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from indiepitcher import (
    CreateMailingListPortalSession,
    IndiePitcherAsyncClient,
    IndiePitcherResponseError,
)

# Load environment variables from .env file
load_dotenv()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[IndiePitcherAsyncClient, None]:
    """Create a test async client with API key from environment."""
    api_key = os.environ.get("INDIEPITCHER_API_KEY", "test_api_key")
    client = IndiePitcherAsyncClient(api_key=api_key)
    yield client
    await client.close()  # Ensure client is closed after test


@pytest_asyncio.fixture(autouse=True)
async def sleep_after_test():
    """Sleep for 1 second after each test."""
    yield  # This allows the test to run
    await asyncio.sleep(1)  # Use asyncio.sleep for async tests


@pytest.mark.asyncio
async def test_invalid_api_key():
    """Test async client initialization with an invalid API key."""
    client = IndiePitcherAsyncClient(api_key="xxx")
    with pytest.raises(IndiePitcherResponseError):
        await client.list_mailing_lists()
    await client.close()  # Manually close since not using fixture


@pytest.mark.asyncio
async def test_list_mailing_lists(async_client: IndiePitcherAsyncClient) -> None:
    """Test listing mailing lists with async client."""
    response = await async_client.list_mailing_lists()
    assert len(response.data) == 3


@pytest.mark.asyncio
async def test_create_mailing_list_management_session(
    async_client: IndiePitcherAsyncClient,
) -> None:
    """Test creating a list management session with async client"""
    response = await async_client.create_mailing_list_portal_session(
        CreateMailingListPortalSession(
            contact_email="petr@indiepitcher.com", return_url="https://indiepitcher.com"
        )
    )
    assert response.data.return_url == "https://indiepitcher.com"
