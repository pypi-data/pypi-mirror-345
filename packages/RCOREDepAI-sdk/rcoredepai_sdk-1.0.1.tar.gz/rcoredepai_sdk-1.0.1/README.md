# RCOREDepAI-sdk

Python SDK & CLI for minting and upgrading DePAI Brain NFTs.

## Install

```bash
pip install RCOREDepAI-sdk
```

## Configure

Create a `.env` in project root:

```
RPC_URL=https://sepolia.infura.io/v3/…
CONTRACT_ADDRESS=0x…
STORAGE_PROVIDER=pinata    # or web3, nft
PINATA_API_KEY=…
PINATA_API_SECRET=…
WEB3_STORAGE_TOKEN=…
NFT_STORAGE_TOKEN=…
PRIVATE_KEY=0x…
```

## Quickstart

```python
from rcoredepai_sdk.storage import get_storage
from rcoredepai_sdk.client import BrainClient
from eth_account import Account

acct    = Account.from_key("0x…")
storage = get_storage()           # reads STORAGE_PROVIDER
client  = BrainClient(storage)

# Read your ONNX file
with open("model.onnx","rb") as f:
    onnx_bytes = f.read()

metadata = {
  "name":               "DePAI Brain by me",
  "description":        "Modular AI NFT",
  "model":              {},
  "skills":             ["Vision","Grip"],
  "performanceRank":    85
}

txh, confirmed = client.mint_brain(onnx_bytes, metadata, acct)
print("Tx hash:", txh)
```