# IndiePitcher Python SDK

Official Python SDK for [IndiePitcher](https://indiepitcher.com)

## Installation

```bash
# Install with pip
pip install indiepitcher

# Or install with uv (recommended)
uv pip install indiepitcher
```

## Quick Start

```python
from indiepitcher import IndiePitcherClient, SendEmail, EmailBodyFormat

# Initialize the client with your API key
client = IndiePitcherClient(api_key="your_api_key")

# or for async environments
# client = IndiePitcherAsyncClient(api_key="your_api_key")

# Send a transactional email
email = SendEmail(
    to="recipient@example.com",
    subject="Hello from IndiePitcher!",
    body="This is a **markdown** email sent via the IndiePitcher Python SDK.",
    body_format=EmailBodyFormat.MARKDOWN
)

response = client.send_email(email)
print(f"Email sent successfully: {response.success}")
```

## Features

- Sync and async variants for all requests
- Send transactional emails with Markdown or HTML content
- Create and manage contacts
- Send emails to contacts or mailing lists
- Create portal sessions for users to manage their subscriptions

## Documentation

For detailed documentation, visit [docs.indiepitcher.com](https://docs.indiepitcher.com).

### Working with Contacts

```python
from indiepitcher import IndiePitcherClient, CreateContact

client = IndiePitcherClient(api_key="your_api_key")

# Create a new contact
contact = CreateContact(
    email="user@example.com",
    name="Example User",
    subscribed_to_lists=["newsletter"],
    custom_properties={"favorite_color": "blue"}
)

response = client.create_contact(contact)

# Get a contact
contact = client.get_contact("user@example.com")
print(contact.data.name)  # "Example User"

# List contacts with pagination
contacts = client.list_contacts(page=1, per_page=50)
for contact in contacts.data:
    print(contact.email)
```

### Sending Emails to Mailing Lists

```python
from indiepitcher import IndiePitcherClient, SendEmailToMailingList, EmailBodyFormat
from datetime import datetime, timedelta

client = IndiePitcherClient(api_key="your_api_key")

# Send an email to a mailing list
email = SendEmailToMailingList(
    subject="Newsletter #1",
    body="# Welcome to our newsletter\n\nThanks for subscribing!",
    body_format=EmailBodyFormat.MARKDOWN,
    list="newsletter",
    track_email_opens=True,
    track_email_link_clicks=True,
    # Schedule the email for future delivery
    delay_until_date=datetime.now() + timedelta(days=1)
)

response = client.send_email_to_mailing_list(email)
```

## Async Support

The SDK also provides an asynchronous client for use in async applications:

```python
import asyncio
from indiepitcher import IndiePitcherAsyncClient, SendEmail, EmailBodyFormat

async def send_email_example():
    async with IndiePitcherAsyncClient(api_key="your_api_key") as client:
        # Send a transactional email
        email = SendEmail(
            to="recipient@example.com",
            subject="Hello from IndiePitcher!",
            body="This is a **markdown** email sent via the IndiePitcher Python SDK.",
            body_format=EmailBodyFormat.MARKDOWN
        )
        
        response = await client.send_email(email)
        return response.success

# Run in an async context
success = asyncio.run(send_email_example())
print(f"Email sent successfully: {success}")
```

The async client supports all the same methods as the synchronous client, but requires the `await` keyword and should be used within an async context.

## Development

### Setting Up the Development Environment

For fast dependency installation, we recommend using UV:

```bash
# Install UV if you don't have it
pip install uv

# Create a virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Run tests
uv run pytest
```

### Testing

```bash
# Run tests
pytest
```

## License

MIT