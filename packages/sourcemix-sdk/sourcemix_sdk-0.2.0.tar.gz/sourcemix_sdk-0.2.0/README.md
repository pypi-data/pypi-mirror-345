# sourcemix-sdk

A simple Python SDK to interact with SourceMix API.

## Installation

```bash
pip install sourcemix-sdk
```

### Usage

```bash
from sourcemix_sdk import SourceMixClient

client = SourceMixClient(api_base="https://www.sourcemix.tech", token="your-jwt-token")
client.document_and_add_to_kb("agent-name", "myproject.zip")
```

