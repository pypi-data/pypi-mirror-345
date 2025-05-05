# Signal Messenger Python API

> **Disclaimer:** This project was generated with the assistance of Claude 3.7 Sonnet based on the Signal CLI REST API [Swagger documentation](https://bbernhard.github.io/signal-cli-rest-api/src/docs/swagger.json).

<p align="center">
  <img src="assets/logo.png" width="200" alt="Signal Messenger Python API Logo">
</p>

[![PyPI version](https://img.shields.io/pypi/v/signal-messenger-python-api.svg)](https://pypi.org/project/signal-messenger-python-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/pcko1/signal-messenger-python-api.svg)](https://github.com/pcko1/signal-messenger-python-api/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/pcko1/signal-messenger-python-api.svg)](https://github.com/pcko1/signal-messenger-python-api/network)
[![GitHub issues](https://img.shields.io/github/issues/pcko1/signal-messenger-python-api.svg)](https://github.com/pcko1/signal-messenger-python-api/issues)
[![Wiki](https://img.shields.io/badge/Wiki-Documentation-blue)](https://github.com/pcko1/signal-messenger-python-api/wiki)

An asynchronous Python wrapper for the [Signal CLI REST API](https://bbernhard.github.io/signal-cli-rest-api/).

## Features

- Fully async implementation using `aiohttp`
- Type hints and dataclasses for better IDE support
- Comprehensive error handling
- Modular design with separate modules for different API endpoints
- Extensive test coverage

## Modules

### Implemented

- **General** - Basic API information and configuration
  - Get API information
  - Get/set API configuration
  - Get/set account settings
  - Health check

- **Devices** - Register and link devices
  - Get linked devices
  - Link a device
  - Get QR code link for device linking
  - Register a device
  - Verify a device

- **Accounts** - Manage Signal accounts
  - Register an account
  - Verify an account
  - Get account details
  - Update an account
  - Set/remove account PIN
  - Delete an account

- **Groups** - Create and manage Signal groups
  - Get groups
  - Create a group
  - Update a group
  - Delete a group
  - Add/remove members
  - Join/leave a group

- **Messages** - Send and receive messages
  - Send messages
  - Get messages
  - Delete messages
  - Send typing indicators
  - Send read/viewed/delivery receipts

- **Attachments** - Handle file attachments
  - Upload attachments
  - Get attachments
  - Delete attachments
  - Get attachment info

- **Profiles** - Manage user profiles
  - Get/update profiles
  - Get contact profiles
  - Set profile sharing

- **Identities** - Handle Signal identities
  - Get identities
  - Trust/verify identities
  - Reset identity sessions

- **Reactions** - Message reactions
  - Send reactions
  - Get reactions
  - Delete reactions

- **Receipts** - Message receipts
  - Get receipts
  - Send read/viewed/delivery receipts

- **Search** - Search functionality
  - Search messages
  - Search contacts
  - Search groups
  - Search all

- **Stickers** - Sticker packs
  - Get sticker packs
  - Install/uninstall sticker packs
  - Upload sticker packs

- **Contacts** - Contact management
  - Get contacts
  - Add/update/delete contacts
  - Block/unblock contacts

## Installation

```bash
pip install signal-messenger-python-api
```

## Prerequisites

Before using this library, you need to have the Signal CLI REST API server running. You can use the Docker image provided by the Signal CLI REST API project:

```bash
docker run -p 9922:8080 -v ~/.signal-cli:/home/.signal-cli bbernhard/signal-cli-rest-api
```

Or using docker-compose:

```yaml
signal:
    image: bbernhard/signal-cli-rest-api:latest
    container_name: signal-cli-rest-api
    ports:
      - 9922:8080
```

For more information, see the [Signal CLI REST API documentation](https://github.com/bbernhard/signal-cli-rest-api).

## Usage

### Basic Usage

```python
import asyncio
from signal_messenger import SignalClient

async def main():
    # Initialize the client with the API base URL
    async with SignalClient("http://localhost:9922") as client:
        # Initialize modules
        await client._init_modules()
        
        # Get API information
        about = await client.get_about()
        print(f"API Version: {about.version}")
        
        # Get API configuration
        config = await client.get_configuration()
        print(f"Logging level: {config.logging.level}")

asyncio.run(main())
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/pcko1/signal-messenger-python-api.git
cd signal-messenger-python-api

# Install dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## License

MIT
