# 1Shot API Python Client

A Python client for the 1Shot API that provides both synchronous and asynchronous interfaces.

## Installation

```bash
pip install uxly-1shot-client
```

## Usage

### Synchronous Client

```python
from uxly_1shot_client import Client

# Initialize the client
client = Client(
    api_key="your_api_key",
    api_secret="your_api_secret",
    base_url="https://api.1shotapi.com/v1"  # Optional, defaults to this URL
)

# List transactions for a business
transactions = client.transactions.list(
    business_id="your_business_id",
    params={"page": 1, "page_size": 10}
)

# Execute a transaction
execution = client.transactions.execute(
    transaction_id="your_transaction_id",
    params={
        "amount": "1000000000000000000",  # 1 ETH in wei
        "recipient": "0x123..."
    }
)

# Get transaction details
transaction = client.transactions.get("your_transaction_id")

# Create a new transaction
new_transaction = client.transactions.create(
    business_id="your_business_id",
    params={
        "name": "Transfer ETH",
        "description": "Transfer ETH to a recipient",
        "chain": 1,  # Ethereum mainnet
        "contract_address": "0x...",
        "function_name": "transfer",
        "state_mutability": "nonpayable",
        "inputs": [
            {
                "name": "recipient",
                "type": "address"
            },
            {
                "name": "amount",
                "type": "uint"
                "type_size": 256
            }
        ]
    }
)
```

### Asynchronous Client

```python
import asyncio
from uxly_1shot_client import AsyncClient

async def main():
    # Initialize the client
    client = AsyncClient(
        api_key="your_api_key",
        api_secret="your_api_secret",
        base_url="https://api.1shotapi.com/v1"  # Optional, defaults to this URL
    )

    # List transactions for a business
    transactions = await client.transactions.list(
        business_id="your_business_id",
        params={"page": 1, "page_size": 10}
    )

    # Execute a transaction
    execution = await client.transactions.execute(
        transaction_id="your_transaction_id",
        params={
            "amount": "1000000000000000000",  # 1 ETH in wei
            "recipient": "0x123..."
        }
    )

    # Get transaction details
    transaction = await client.transactions.get("your_transaction_id")

    # Create a new transaction
    new_transaction = await client.transactions.create(
        business_id="your_business_id",
        params={
            "name": "Transfer ETH",
            "description": "Transfer ETH to a recipient",
            "chain": 1,  # Ethereum mainnet
            "contract_address": "0x...",
            "function_name": "transfer",
            "state_mutability": "nonpayable",
            "inputs": [
                {
                    "name": "recipient",
                    "type": "address"
                },
                {
                    "name": "amount",
                    "type": "uint256"
                }
            ]
        }
    )

# Run the async code
asyncio.run(main())
```

### Webhook Verification

#### Using the Standalone Function

```python
from uxly_1shot_client import verify_webhook
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.post("/webhook")
async def handle_webhook(request: Request):
    # Get the webhook body and signature
    body = await request.json()
    signature = body.pop("signature", None)
    
    if not signature:
        raise HTTPException(status_code=400, detail="Signature missing")
    
    # Your webhook public key
    public_key = "your_webhook_public_key"
    
    try:
        # Verify the webhook signature
        is_valid = verify_webhook(
            body=body,
            signature=signature,
            public_key=public_key
        )
        
        if not is_valid:
            raise HTTPException(status_code=403, detail="Invalid signature")
            
        return {"message": "Webhook verified successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
```

#### Using the WebhookVerifier Class

```python
from uxly_1shot_client import WebhookVerifier
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

# Create a verifier instance with your public key
verifier = WebhookVerifier(public_key="your_webhook_public_key")

@app.post("/webhook")
async def handle_webhook(request: Request):
    # Get the webhook body and signature
    body = await request.json()
    signature = body.pop("signature", None)
    
    if not signature:
        raise HTTPException(status_code=400, detail="Signature missing")
    
    try:
        # Verify the webhook signature
        is_valid = verifier.verify(
            body=body,
            signature=signature
        )
        
        if not is_valid:
            raise HTTPException(status_code=403, detail="Invalid signature")
            
        return {"message": "Webhook verified successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
```

## Error Handling

The client raises exceptions for various error conditions:

- `requests.exceptions.RequestException` for synchronous client errors
- `httpx.HTTPError` for asynchronous client errors
- `ValueError` for invalid parameters
- `InvalidSignature` for invalid webhook signatures

## Type Hints

The client includes comprehensive type hints for better IDE support and type checking. All models and responses are properly typed using Pydantic models.

## Publishing

This package is published to PyPI using modern Python packaging tools. Here's how to publish a new version:

1. Install the required tools:
```bash
pip install hatch hatchling twine
```

2. Update the version in `pyproject.toml`:
```toml
[project]
version = "0.1.0"  # Update this to your new version
```

3. Build the package:
```bash
hatch build
```

4. Test the build:
```bash
# On Windows:
hatch run python -m pip install dist\uxly_1shot_client-1.0.11-py3-none-any.whl

# On Unix-like systems (Linux/macOS):
hatch run python -m pip install dist/uxly_1shot_client-1.0.11-py3-none-any.whl
```

5. Upload to PyPI:
```bash
# First, upload to TestPyPI to verify everything works
twine upload --repository testpypi dist/uxly_1shot_client-1.0.11-py3-none-any.whl dist/uxly_1shot_client-1.0.11.tar.gz

# If everything looks good, upload to the real PyPI
twine upload dist/uxly_1shot_client-1.0.11-py3-none-any.whl dist/uxly_1shot_client-1.0.11.tar.gz
```

Note: You'll need to have a PyPI account and configure your credentials. You can do this by:
1. Creating a `~/.pypirc` file:
```ini
[pypi]
username = your_username
password = your_password
```

Or by using environment variables:
```bash
export TWINE_USERNAME=your_username
export TWINE_PASSWORD=your_password
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 