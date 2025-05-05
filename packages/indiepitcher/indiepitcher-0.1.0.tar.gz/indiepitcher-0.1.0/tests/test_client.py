"""Tests for IndiePitcher client."""

import os
import time

import pytest
from dotenv import load_dotenv

from indiepitcher import (
    CreateMailingListPortalSession,
    IndiePitcherClient,
    IndiePitcherResponseError,
)

# Load environment variables from .env file
load_dotenv()


@pytest.fixture
def client() -> IndiePitcherClient:
    """Create a test client with API key from environment."""
    api_key = os.environ.get("INDIEPITCHER_API_KEY", "test_api_key")
    return IndiePitcherClient(api_key=api_key)


@pytest.fixture(autouse=True)
def sleep_after_test():
    """Sleep for 1 second after each test."""
    yield  # This allows the test to run
    time.sleep(
        1
    )  # Then sleeps for 1 second after the test completes to work around rate limiting


def test_invalid_api_key():
    """Test client initialization with an invalid API key."""

    client = IndiePitcherClient(api_key="xxx")
    with pytest.raises(IndiePitcherResponseError):
        client.list_mailing_lists()


def test_list_mailing_lists(client: IndiePitcherClient) -> None:
    """Test listing mailing lists."""

    response = client.list_mailing_lists()
    assert len(response.data) == 3


def test_create_mailing_list_management_session(client: IndiePitcherClient) -> None:
    """Test creating a list management session"""

    response = client.create_mailing_list_portal_session(
        CreateMailingListPortalSession(
            contact_email="petr@indiepitcher.com", return_url="https://indiepitcher.com"
        )
    )

    assert response.data.return_url == "https://indiepitcher.com"
