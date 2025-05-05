import pytest
from rcoredepai_sdk.client import BrainClient
from rcoredepai_sdk.storage import PinataProvider

def test_client_init():
    storage = PinataProvider()
    client = BrainClient(storage)
    assert hasattr(client, 'mint_brain')
