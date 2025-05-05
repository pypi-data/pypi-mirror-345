from typing import List

import httpx

from .models import (
    BaseIndiePitcherModel,
    Contact,
    CreateContact,
    CreateMailingListPortalSession,
    DataResponse,
    EmptyResponse,
    IndiePitcherResponseError,
    MailingList,
    MailingListPortalSession,
    PagedDataResponse,
    SendEmail,
    SendEmailToContact,
    SendEmailToMailingList,
    UpdateContact,
)


class ErrorResponse(BaseIndiePitcherModel):
    reason: str


def raise_for_invalid_status(response: httpx.Response) -> None:
    if response.status_code >= 400:
        decoded_response = ErrorResponse.model_validate_json(response.content)
        raise IndiePitcherResponseError(
            status_code=response.status_code, reason=decoded_response.reason
        )


class IndiePitcherAsyncClient:
    """Async client for interacting with the IndiePitcher API."""

    def __init__(
        self, api_key: str, base_url: str = "https://api.indiepitcher.com/v1"
    ) -> None:
        """
        Initialize the IndiePitcher async API client.

        Args:
            api_key: Your IndiePitcher API key
            base_url: Base URL for the IndiePitcher API (default: https://api.indiepitcher.com/v1)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "IndiePitcher-Python/0.1.0",
            },
            timeout=30.0,  # Default timeout of 30 seconds
        )

    async def __aenter__(self):
        """Support async context manager protocol."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close the client when exiting context manager."""
        await self.close()

    async def close(self):
        """Close the underlying HTTP client."""
        await self.client.aclose()

    # Contact Management

    async def get_contact(self, email: str) -> DataResponse[Contact]:
        """
        Find a contact by email.

        Args:
            email: The email address of the contact to find

        Returns:
            DataResponse[Contact]: The contact if found

        Raises:
            indiepitcher.IndiePitcherResponseError: If the request fails
        """
        response = await self.client.get(
            f"{self.base_url}/contacts/find", params={"email": email}
        )
        raise_for_invalid_status(response)
        return DataResponse[Contact].model_validate_json(response.content)

    async def list_contacts(
        self, page: int = 1, per_page: int = 20
    ) -> PagedDataResponse[Contact]:
        """
        List contacts with pagination.

        Args:
            page: Page number (default: 1)
            per_page: Number of contacts per page (default: 20)

        Returns:
            PagedDataResponse[Contact]: Paginated list of contacts

        Raises:
            indiepitcher.IndiePitcherResponseError: If the request fails
        """
        response = await self.client.get(
            f"{self.base_url}/contacts", params={"page": page, "per": per_page}
        )
        raise_for_invalid_status(response)
        return PagedDataResponse[Contact].model_validate_json(response.content)

    async def create_contact(self, contact: CreateContact) -> DataResponse[Contact]:
        """
        Add a new contact.

        Args:
            contact: Contact details to create

        Returns:
            DataResponse[Contact]: The created contact

        Raises:
            indiepitcher.IndiePitcherResponseError: If the request fails
        """
        response = await self.client.post(
            f"{self.base_url}/contacts/create",
            json=contact.model_dump(by_alias=True, exclude_none=True),
        )
        raise_for_invalid_status(response)
        return DataResponse[Contact].model_validate_json(response.content)

    async def create_contacts(
        self, contacts: List[CreateContact]
    ) -> DataResponse[Contact]:
        """
        Add multiple contacts in a single request.

        Args:
            contacts: List of contacts to create (max 100)

        Returns:
            DataResponse[Contact]: The created contacts

        Raises:
            indiepitcher.IndiePitcherResponseError: If the request fails
            ValueError: If more than 100 contacts are provided
        """

        response = await self.client.post(
            f"{self.base_url}/contacts/create_many",
            json=[
                contact.model_dump(by_alias=True, exclude_none=True)
                for contact in contacts
            ],
        )
        raise_for_invalid_status(response)
        return DataResponse[Contact].model_validate_json(response.content)

    async def update_contact(self, contact: UpdateContact) -> DataResponse[Contact]:
        """
        Update an existing contact.

        Args:
            contact: Contact details to update

        Returns:
            DataResponse[Contact]: The updated contact

        Raises:
            indiepitcher.IndiePitcherResponseError: If the request fails
        """
        response = await self.client.patch(
            f"{self.base_url}/contacts/update",
            json=contact.model_dump(by_alias=True, exclude_none=True),
        )
        raise_for_invalid_status(response)
        return DataResponse[Contact].model_validate_json(response.content)

    async def delete_contact(self, email: str) -> EmptyResponse:
        """
        Delete a contact by email.

        Args:
            email: Email address of the contact to delete

        Returns:
            EmptyResponse: Success response

        Raises:
            indiepitcher.IndiePitcherResponseError: If the request fails
        """
        response = await self.client.post(
            f"{self.base_url}/contacts/delete", json={"email": email}
        )
        raise_for_invalid_status(response)
        return EmptyResponse.model_validate_json(response.content)

    # Mailing List Management

    async def list_mailing_lists(
        self, page: int = 1, per_page: int = 10
    ) -> PagedDataResponse[MailingList]:
        """
        Get all mailing lists.

        Args:
            page: Page number (default: 1)
            per_page: Number of lists per page (default: 10)

        Returns:
            PagedDataResponse[MailingList]: Paginated list of mailing lists

        Raises:
            indiepitcher.IndiePitcherResponseError: If the request fails
        """
        response = await self.client.get(
            f"{self.base_url}/lists", params={"page": page, "per": per_page}
        )
        raise_for_invalid_status(response)
        return PagedDataResponse[MailingList].model_validate_json(response.content)

    async def create_mailing_list_portal_session(
        self, session: CreateMailingListPortalSession
    ) -> DataResponse[MailingListPortalSession]:
        """
        Create a mailing list portal session.

        Args:
            session: Portal session details

        Returns:
            MailingListPortalSessionResponse: Portal session details with URL

        Raises:
            indiepitcher.IndiePitcherResponseError: If the request fails
        """

        response = await self.client.post(
            f"{self.base_url}/lists/portal_session",
            json=session.model_dump(by_alias=True, exclude_none=True),
        )
        raise_for_invalid_status(response)
        return DataResponse[MailingListPortalSession].model_validate_json(
            response.content
        )

    # Email Sending

    async def send_email(self, email: SendEmail) -> EmptyResponse:
        """
        Send a transactional email.

        Args:
            email: Email details to send

        Returns:
            EmptyResponse: Success response

        Raises:
            indiepitcher.IndiePitcherResponseError: If the request fails
        """
        response = await self.client.post(
            f"{self.base_url}/email/transactional",
            json=email.model_dump(by_alias=True, exclude_none=True),
        )
        raise_for_invalid_status(response)
        return EmptyResponse.model_validate_json(response.content)

    async def send_email_to_contact(self, email: SendEmailToContact) -> EmptyResponse:
        """
        Send an email to one or more contacts.

        Args:
            email: Email details to send

        Returns:
            EmptyResponse: Success response

        Raises:
            indiepitcher.IndiePitcherResponseError: If the request fails
        """
        response = await self.client.post(
            f"{self.base_url}/email/contact",
            json=email.model_dump(by_alias=True, exclude_none=True),
        )
        raise_for_invalid_status(response)
        return EmptyResponse.model_validate_json(response.content)

    async def send_email_to_mailing_list(
        self, email: SendEmailToMailingList
    ) -> EmptyResponse:
        """
        Send an email to a mailing list.

        Args:
            email: Email details to send

        Returns:
            EmptyResponse: Success response

        Raises:
            indiepitcher.IndiePitcherResponseError: If the request fails
        """
        response = await self.client.post(
            f"{self.base_url}/email/list",
            json=email.model_dump(by_alias=True, exclude_none=True),
        )
        raise_for_invalid_status(response)
        return EmptyResponse.model_validate_json(response.content)
