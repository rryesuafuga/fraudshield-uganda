#!/usr/bin/env python3
"""
FraudShield Uganda - Model Download Script

Downloads open-source fraud detection ML models on-demand.
Models are stored locally in the 'downloaded/' subfolder.

Usage:
    python download_models.py --list           # List available models
    python download_models.py --all            # Download all models
    python download_models.py --model NAME     # Download specific model
    python download_models.py --info NAME      # Show model details
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Base directory for downloaded models
MODELS_DIR = Path(__file__).parent / "downloaded"

# Available models registry
MODELS = {
    "huggingface-fraud": {
        "name": "HuggingFace Fraud Detection",
        "source": "huggingface",
        "repo_id": "vaibhav07112004/Fraud-detection",
        "description": "Pre-trained binary classifier for general fraud detection",
        "size": "~500MB",
        "requirements": ["transformers", "torch"],
    },
    "huggingface-creditcard": {
        "name": "HuggingFace Credit Card Fraud",
        "source": "huggingface",
        "repo_id": "vaibhav07112004/Credit_card_fraud_detection",
        "description": "Specialized model for credit card transaction fraud",
        "size": "~450MB",
        "requirements": ["transformers", "torch"],
    },
    "keras-autoencoder": {
        "name": "Keras Autoencoder",
        "source": "github",
        "repo_url": "https://github.com/esenthil/fraud_detection",
        "description": "Unsupervised anomaly detection using autoencoders",
        "size": "~50MB",
        "requirements": ["tensorflow", "keras"],
    },
    "pyod-isolation-forest": {
        "name": "PyOD Isolation Forest",
        "source": "pypi",
        "package": "pyod",
        "description": "Fast anomaly detection algorithm, good for tabular data",
        "size": "~10MB",
        "requirements": ["pyod", "scikit-learn"],
    },
    "pyod-autoencoder": {
        "name": "PyOD AutoEncoder",
        "source": "pypi",
        "package": "pyod",
        "description": "Neural network-based anomaly detection",
        "size": "~10MB",
        "requirements": ["pyod", "tensorflow"],
    },
    "tazama-rules": {
        "name": "Tazama Platform Rules",
        "source": "github",
        "repo_url": "https://github.com/tazama-lf/tazama",
        "description": "Complete fraud monitoring platform with rules engine",
        "size": "~100MB",
        "requirements": ["nodejs"],
    },
    "onnx-lstm": {
        "name": "ONNX LSTM Classifier",
        "source": "github",
        "repo_url": "https://github.com/onnx/models",
        "description": "LSTM model for sequential transaction analysis",
        "size": "~200MB",
        "requirements": ["onnxruntime"],
    },
}


def ensure_dir(path: Path) -> None:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def check_requirements(requirements: list) -> bool:
    """Check if required packages are installed."""
    missing = []
    for req in requirements:
        try:
            __import__(req.replace("-", "_"))
        except ImportError:
            missing.append(req)

    if missing:
        print(f"  Missing packages: {', '.join(missing)}")
        print(f"  Install with: pip install {' '.join(missing)}")
        return False
    return True


def download_huggingface(model_info: dict, target_dir: Path) -> bool:
    """Download model from HuggingFace Hub."""
    try:
        from huggingface_hub import snapshot_download

        print(f"  Downloading from HuggingFace: {model_info['repo_id']}")
        snapshot_download(
            repo_id=model_info["repo_id"],
            local_dir=target_dir,
            local_dir_use_symlinks=False,
        )
        return True
    except ImportError:
        print("  Error: huggingface_hub not installed")
        print("  Install with: pip install huggingface_hub")
        return False
    except Exception as e:
        print(f"  Error downloading: {e}")
        return False


def download_github(model_info: dict, target_dir: Path) -> bool:
    """Clone repository from GitHub."""
    try:
        repo_url = model_info["repo_url"]
        print(f"  Cloning from GitHub: {repo_url}")

        if target_dir.exists():
            print(f"  Directory already exists, pulling latest...")
            subprocess.run(
                ["git", "-C", str(target_dir), "pull"],
                check=True,
                capture_output=True,
            )
        else:
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(target_dir)],
                check=True,
                capture_output=True,
            )
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Error cloning: {e}")
        return False


def download_pypi(model_info: dict, target_dir: Path) -> bool:
    """Install package from PyPI and create usage example."""
    try:
        package = model_info["package"]
        print(f"  Installing from PyPI: {package}")

        subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            check=True,
            capture_output=True,
        )

        # Create usage example file
        ensure_dir(target_dir)
        example_file = target_dir / "usage_example.py"

        if package == "pyod":
            example_file.write_text('''"""
PyOD Usage Example for FraudShield Uganda
"""
from pyod.models.iforest import IForest
from pyod.models.auto_encoder import AutoEncoder
import numpy as np

# Sample data (replace with your transaction features)
X_train = np.random.randn(1000, 10)  # 1000 samples, 10 features

# Isolation Forest
clf_iforest = IForest(contamination=0.1)
clf_iforest.fit(X_train)

# Get anomaly scores
scores = clf_iforest.decision_scores_

# Predict on new data
X_new = np.random.randn(100, 10)
predictions = clf_iforest.predict(X_new)  # 0: normal, 1: anomaly
''')

        print(f"  Created usage example: {example_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Error installing: {e}")
        return False


def download_model(model_key: str) -> bool:
    """Download a specific model."""
    if model_key not in MODELS:
        print(f"Error: Unknown model '{model_key}'")
        print(f"Available models: {', '.join(MODELS.keys())}")
        return False

    model_info = MODELS[model_key]
    target_dir = MODELS_DIR / model_key

    print(f"\nDownloading: {model_info['name']}")
    print(f"  Description: {model_info['description']}")
    print(f"  Size: {model_info['size']}")
    print(f"  Target: {target_dir}")

    # Check requirements
    if not check_requirements(model_info.get("requirements", [])):
        response = input("  Continue anyway? [y/N]: ")
        if response.lower() != "y":
            return False

    ensure_dir(MODELS_DIR)

    # Download based on source type
    source = model_info["source"]
    if source == "huggingface":
        return download_huggingface(model_info, target_dir)
    elif source == "github":
        return download_github(model_info, target_dir)
    elif source == "pypi":
        return download_pypi(model_info, target_dir)
    else:
        print(f"  Unknown source type: {source}")
        return False


def list_models() -> None:
    """List all available models."""
    print("\nAvailable Models for FraudShield Uganda:")
    print("=" * 60)

    for key, info in MODELS.items():
        status = "Downloaded" if (MODELS_DIR / key).exists() else "Not downloaded"
        print(f"\n  {key}")
        print(f"    Name: {info['name']}")
        print(f"    Description: {info['description']}")
        print(f"    Size: {info['size']}")
        print(f"    Status: [{status}]")


def show_info(model_key: str) -> None:
    """Show detailed information about a model."""
    if model_key not in MODELS:
        print(f"Error: Unknown model '{model_key}'")
        return

    info = MODELS[model_key]
    print(f"\nModel: {info['name']}")
    print("=" * 60)
    print(f"Key: {model_key}")
    print(f"Description: {info['description']}")
    print(f"Source: {info['source']}")
    print(f"Size: {info['size']}")
    print(f"Requirements: {', '.join(info.get('requirements', []))}")

    if info["source"] == "huggingface":
        print(f"HuggingFace Repo: {info['repo_id']}")
    elif info["source"] == "github":
        print(f"GitHub URL: {info['repo_url']}")
    elif info["source"] == "pypi":
        print(f"PyPI Package: {info['package']}")

    target_dir = MODELS_DIR / model_key
    if target_dir.exists():
        print(f"\nLocal Path: {target_dir}")
        print("Status: Downloaded")
    else:
        print("\nStatus: Not downloaded")
        print(f"Download with: python download_models.py --model {model_key}")


def download_all() -> None:
    """Download all available models."""
    print("\nDownloading all models...")
    print("This may take a while and require significant disk space.")

    response = input("Continue? [y/N]: ")
    if response.lower() != "y":
        print("Aborted.")
        return

    success = 0
    failed = 0

    for model_key in MODELS:
        if download_model(model_key):
            success += 1
        else:
            failed += 1

    print(f"\nCompleted: {success} succeeded, {failed} failed")


def main():
    parser = argparse.ArgumentParser(
        description="Download fraud detection ML models for FraudShield Uganda"
    )
    parser.add_argument(
        "--list", action="store_true", help="List available models"
    )
    parser.add_argument(
        "--model", type=str, help="Download specific model by key"
    )
    parser.add_argument(
        "--all", action="store_true", help="Download all models"
    )
    parser.add_argument(
        "--info", type=str, help="Show detailed info about a model"
    )

    args = parser.parse_args()

    if args.list:
        list_models()
    elif args.model:
        download_model(args.model)
    elif args.all:
        download_all()
    elif args.info:
        show_info(args.info)
    else:
        parser.print_help()
        print("\nExample usage:")
        print("  python download_models.py --list")
        print("  python download_models.py --model huggingface-fraud")
        print("  python download_models.py --info pyod-isolation-forest")


if __name__ == "__main__":
    main()
