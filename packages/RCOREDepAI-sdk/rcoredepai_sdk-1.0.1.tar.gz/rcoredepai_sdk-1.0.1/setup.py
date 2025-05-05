from setuptools import setup, find_packages

setup(
    name="RCOREDepAI-sdk",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[
        "web3>=6.20.0",
        "eth-account",
        "python-dotenv",
        "requests",
        "click",
        "onnxruntime",
        "numpy",
    ],
    entry_points={
        "console_scripts": [
            "rcoredepai=rcoredepai_sdk.cli:cli"
        ],
    },
)
