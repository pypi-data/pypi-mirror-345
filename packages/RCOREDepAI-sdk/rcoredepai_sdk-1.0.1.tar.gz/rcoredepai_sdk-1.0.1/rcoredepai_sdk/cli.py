import click
from eth_account import Account
from rcoredepai_sdk.client import BrainClient
from rcoredepai_sdk.storage import get_storage

@click.group()
def cli():
    """RCOREDepAI SDK CLI"""
    pass

@cli.command()
@click.argument("onnx_path", type=click.Path(exists=True))
@click.argument("skills", nargs=-1)
@click.argument("rank", type=int)
@click.option("--provider", default=None, help="pinata|web3|nft")
@click.option("--pk", envvar="PRIVATE_KEY", prompt=True, hide_input=True)
def mint(onnx_path, skills, rank, provider, pk):
    """Mint a new Brain NFT."""
    acct    = Account.from_key(pk)
    data    = open(onnx_path, "rb").read()
    metadata = {
        "name":            f"DePAI Brain by {acct.address}",
        "description":     "Modular AI NFT",
        "model":           {},
        "skills":          list(skills),
        "performanceRank": rank
    }
    client  = BrainClient(get_storage(provider))
    txh, ok = client.mint_brain(data, metadata, acct)
    click.echo(f"→ Tx: https://etherscan.io/tx/{txh}")
    if not ok:
        click.echo("⏳ Transaction pending…")
