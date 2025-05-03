# Velatir Python SDK

[![PyPI version](https://badge.fury.io/py/velatir.svg)](https://badge.fury.io/py/velatir)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This is the official Python SDK for [Velatir](https://velatir.com), a service that allows you to monitor and approve/reject AI function calls.

## Installation

```bash
pip install velatir
```

## Quick Start

```python
import velatir

# Initialize the SDK with your API key
velatir.init(api_key="your-api-key")

# Decorate functions you want to monitor
@velatir.watch()
async def send_email(to: str, subject: str, body: str):
    """Send an email to the customer"""
    print(f"Sending email to {to}: {subject}")
    # Your email sending logic here
    
# Call the function as usual (or from LLM tool)
await send_email("customer@example.com", "Welcome!", "Hello from Velatir!")
```

## How It Works

The `@velatir.watch()` decorator intercepts function calls and:

1. Sends the function details and arguments to the Velatir API
2. Processes the API response:
   - If `approved`: The function runs immediately
   - If `pending`: The SDK polls the API every 5 seconds until the request is approved or denied
   - If `denied`: An exception is raised and the function doesn't run

## Features

- Monitor function calls in real-time
- Approve or reject function execution
- Automatically handle pending approval states
- Works with both synchronous and asynchronous functions
- Customizable polling intervals and timeout settings

## Advanced Usage

### Custom Polling Configuration

```python
@velatir.watch(polling_interval=2.0, max_attempts=30)
async def delete_user(user_id: str):
    """Delete a user from the system"""
    # Deletion logic here
```

### Adding Metadata

```python
@velatir.watch(metadata={"priority": "high", "team": "billing"})
async def charge_credit_card(card_id: str, amount: float):
    """Charge a customer's credit card"""
    # Charging logic here
```

### Logging and Retries

The SDK supports configurable logging and automatic retries for network failures:

```python
import velatir
import logging
from velatir import LogLevel

# Configure Python's logging (optional)
logging.basicConfig(level=logging.INFO)

# Configure with logging and retries
velatir.init(
    api_key="your-api-key",
    log_level=LogLevel.INFO,  # Or use int: 0=NONE, 1=ERROR, 2=INFO, 3=DEBUG
    max_retries=3,            # Number of retries for failed requests
    retry_backoff=0.5         # Base backoff time (exponential)
)

# Configure Velatir's logger specifically (optional)
velatir.configure_logging(level=logging.INFO)
```

### Synchronous Client

While the decorator works with both async and sync functions, you can also use the synchronous client methods directly:

```python
# Get the global client
client = velatir.get_client()

# Create a watch request synchronously
response = client.create_watch_request_sync(
    function_name="charge_card",
    args={"card_id": "card_123", "amount": 99.99},
    metadata={"priority": "high"}
)

# Wait for approval synchronously
if response.is_pending:
    approval = client.wait_for_approval_sync(
        request_id=response.request_id,
        polling_interval=2.0
    )
```

## Error Handling

When a function is denied:

```python
try:
    await risky_function()
except velatir.VelatirWatchDeniedError as e:
    print(f"Function was denied: {e}")
```

## Documentation

For detailed documentation, visit [https://docs.velatir.com](https://docs.velatir.com)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.