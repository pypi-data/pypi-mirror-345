import os
import pytest
from rcoredepai_sdk.storage import get_storage, PinataProvider, Web3StorageProvider, NFTStorageProvider

def test_default_storage(monkeypatch):
    monkeypatch.delenv('STORAGE_PROVIDER', raising=False)
    provider = get_storage()
    assert isinstance(provider, PinataProvider)

def test_web3_storage(monkeypatch):
    monkeypatch.setenv('STORAGE_PROVIDER','web3')
    provider = get_storage()
    assert isinstance(provider, Web3StorageProvider)

def test_nft_storage(monkeypatch):
    monkeypatch.setenv('STORAGE_PROVIDER','nft')
    provider = get_storage()
    assert isinstance(provider, NFTStorageProvider)
