import os
import requests
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()

class StorageProvider(ABC):
    @abstractmethod
    def pin_file(self, data: bytes, name: str) -> str: ...
    @abstractmethod
    def pin_json(self, obj: dict) -> str: ...

class PinataProvider(StorageProvider):
    API_BASE = "https://api.pinata.cloud"
    def __init__(self):
        self.key    = os.getenv("PINATA_API_KEY")
        self.secret = os.getenv("PINATA_API_SECRET")
    def pin_file(self, data, name):
        url = f"{self.API_BASE}/pinning/pinFileToIPFS"
        headers = {"pinata_api_key": self.key, "pinata_secret_api_key": self.secret}
        files = {"file": (name, data)}
        r = requests.post(url, files=files, headers=headers)
        r.raise_for_status(); return r.json()["IpfsHash"]
    def pin_json(self, obj):
        url = f"{self.API_BASE}/pinning/pinJSONToIPFS"
        headers = {"pinata_api_key": self.key, "pinata_secret_api_key": self.secret}
        r = requests.post(url,
            json={"pinataOptions":{"cidVersion":1},"pinataContent":obj},
            headers=headers
        )
        r.raise_for_status(); return r.json()["IpfsHash"]

class Web3StorageProvider(StorageProvider):
    API_BASE = "https://api.web3.storage"
    def __init__(self):
        self.token = os.getenv("WEB3_STORAGE_TOKEN")
    def pin_file(self, data, name):
        url = f"{self.API_BASE}/upload"
        headers = {"Authorization": f"Bearer {self.token}"}
        files   = {"file": (name, data)}
        r       = requests.post(url, files=files, headers=headers)
        r.raise_for_status(); return r.json()["cid"]
    def pin_json(self, obj):
        import json
        return self.pin_file(json.dumps(obj).encode(), "meta.json")

class NFTStorageProvider(StorageProvider):
    API_BASE = "https://api.nft.storage"
    def __init__(self):
        self.token = os.getenv("NFT_STORAGE_TOKEN")
    def pin_file(self, data, name):
        url = f"{self.API_BASE}/upload"
        headers = {"Authorization": f"Bearer {self.token}"}
        files   = {"file": (name, data)}
        r       = requests.post(url, files=files, headers=headers)
        r.raise_for_status(); return r.json()["value"]["cid"]
    def pin_json(self, obj):
        import json
        return self.pin_file(json.dumps(obj).encode(), "meta.json")

def get_storage(provider_name=None):
    name = (provider_name or os.getenv("STORAGE_PROVIDER", "pinata")).lower()
    if name == "pinata": return PinataProvider()
    if name == "web3":   return Web3StorageProvider()
    if name == "nft":    return NFTStorageProvider()
    raise ValueError(f"Unknown storage provider: {name}")
