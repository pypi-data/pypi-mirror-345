import os
import time
from web3 import Web3
from web3.exceptions import TimeExhausted
from eth_utils import to_checksum_address
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("RPC_URL", "")
# fallback to a zero‐address if no CONTRACT_ADDRESS is defined
raw_contract = os.getenv("CONTRACT_ADDRESS") or "0x0000000000000000000000000000000000000000"
CONTRACT_ADDR = to_checksum_address(raw_contract)
ABI_PATH      = os.path.join(os.path.dirname(__file__), "..", "abi.json")

class BrainClient:
    def __init__(self, storage):
        self.w3       = Web3(Web3.HTTPProvider(RPC_URL))
        # Only error if an RPC_URL was provided but we failed to connect
        if RPC_URL and not self.w3.is_connected():
            raise ConnectionError(f"Cannot connect to {RPC_URL!r}")
        with open(ABI_PATH) as f:
            abi = f.read()
        self.contract = self.w3.eth.contract(address=CONTRACT_ADDR, abi=abi)
        self.storage  = storage

    def _send_tx(self, fn, account):
        tx = fn.build_transaction({
            "chainId":    self.w3.eth.chain_id,
            "from":       account.address,
            "nonce":      self.w3.eth.get_transaction_count(account.address),
            "gasPrice":   self.w3.eth.gas_price,
            "gas":        fn.estimate_gas({"from": account.address}) * 2
        })
        signed = account.sign_transaction(tx)
        txh    = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        try:
            self.w3.eth.wait_for_transaction_receipt(txh, timeout=120)
            return txh.hex(), True
        except TimeExhausted:
            return txh.hex(), False

    def mint_brain(self, model_bytes, metadata, account):
        mcid = self.storage.pin_file(model_bytes, "model.onnx")
        metadata["model"]["cid"] = mcid
        mid  = self.storage.pin_json(metadata)
        uri  = f"ipfs://{mid}"
        fn   = self.contract.functions.mintBrain(
                    mid,
                    metadata["skills"],
                    metadata["performanceRank"],
                    uri
               )
        return self._send_tx(fn, account)

    def upgrade_brain(self, token_id, model_bytes, metadata, account):
        mcid = self.storage.pin_file(model_bytes, f"upgrade_{token_id}.onnx")
        metadata["model"]["cid"] = mcid
        mid  = self.storage.pin_json(metadata)
        uri  = f"ipfs://{mid}"
        fn   = self.contract.functions.upgradeBrain(
                    token_id,
                    metadata["skills"],
                    metadata["performanceRank"],
                    uri
               )
        return self._send_tx(fn, account)

    def get_balance(self, address):
        wei = self.w3.eth.get_balance(address)
        return self.w3.from_wei(wei, "ether")
