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
    # ===== WASM/WebGPU Browser Models =====
    "ibm-fraud-onnx": {
        "name": "IBM ai-on-z Fraud Detection (ONNX)",
        "source": "github",
        "repo_url": "https://github.com/IBM/ai-on-z-fraud-detection",
        "description": "LSTM/GRU models for credit card fraud, ONNX format for browser deployment",
        "size": "~100MB",
        "requirements": ["onnxruntime"],
        "wasm_compatible": True,
        "input_shape": "(7, 16, 220)",
    },
    "hazelcast-fraud-onnx": {
        "name": "Hazelcast LightGBM Fraud (ONNX)",
        "source": "github",
        "repo_url": "https://github.com/hazelcast/fraud-detection-onnx",
        "description": "LightGBM ONNX model with <0.1ms inference, 15 features",
        "size": "~5MB",
        "requirements": ["onnxruntime"],
        "wasm_compatible": True,
        "input_shape": "(1, 15)",
    },
    "vaibhav-fraud-collection": {
        "name": "Vaibhav Singh Fraud Models (11 models)",
        "source": "huggingface",
        "repo_id": "vaibhav07112004/fraud-detection-models",
        "description": "Collection of 11 specialized fraud models (credit card, QR, e-commerce, etc.)",
        "size": "~200MB",
        "requirements": ["scikit-learn", "skl2onnx"],
        "wasm_compatible": True,
        "note": "Requires sklearn-onnx conversion for WASM deployment",
    },
    "onnx-runtime-web": {
        "name": "ONNX Runtime Web (npm)",
        "source": "npm",
        "package": "onnxruntime-web",
        "description": "Browser inference engine with WASM/WebGL/WebGPU support",
        "size": "~15MB",
        "requirements": [],
        "wasm_compatible": True,
    },
    "tract-rust": {
        "name": "tract (Rust ONNX Runtime)",
        "source": "cargo",
        "package": "tract-onnx",
        "description": "Pure Rust ONNX inference, compiles to WASM natively",
        "size": "~5MB",
        "requirements": [],
        "wasm_compatible": True,
    },
    "candle-wasm": {
        "name": "candle (HuggingFace Rust)",
        "source": "github",
        "repo_url": "https://github.com/huggingface/candle",
        "description": "Rust ML framework with first-class WASM support, 17k+ stars",
        "size": "~50MB",
        "requirements": [],
        "wasm_compatible": True,
    },
    "burn-wgpu": {
        "name": "burn (Rust WebGPU)",
        "source": "github",
        "repo_url": "https://github.com/tracel-ai/burn",
        "description": "Rust ML with native WebGPU backend, ~2MB WASM output",
        "size": "~30MB",
        "requirements": [],
        "wasm_compatible": True,
    },
    "tfjs-webgpu": {
        "name": "TensorFlow.js WebGPU",
        "source": "npm",
        "package": "@tensorflow/tfjs",
        "description": "TensorFlow.js with WebGPU backend, 3x faster than WebGL",
        "size": "~20MB",
        "requirements": [],
        "wasm_compatible": True,
    },
    "smartcore-wasm": {
        "name": "smartcore (Rust ML for WASM)",
        "source": "cargo",
        "package": "smartcore",
        "description": "Random Forests, SVM, Decision Trees - WASM-first design",
        "size": "~2MB",
        "requirements": [],
        "wasm_compatible": True,
    },
    "linfa-rust": {
        "name": "linfa (Rust scikit-learn)",
        "source": "github",
        "repo_url": "https://github.com/rust-ml/linfa",
        "description": "Rust ML toolkit, 3.4k+ stars, no BLAS dependency for WASM",
        "size": "~20MB",
        "requirements": [],
        "wasm_compatible": True,
    },
    "extended-isolation-forest": {
        "name": "Extended Isolation Forest (Rust)",
        "source": "cargo",
        "package": "extended-isolation-forest",
        "description": "Anomaly detection algorithm in pure Rust, targets WASM directly",
        "size": "~1MB",
        "requirements": [],
        "wasm_compatible": True,
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


def download_npm(model_info: dict, target_dir: Path) -> bool:
    """Install npm package and create usage example."""
    try:
        package = model_info["package"]
        print(f"  NPM Package: {package}")
        print(f"  Install with: npm install {package}")

        # Create usage example
        ensure_dir(target_dir)
        example_file = target_dir / "usage_example.js"

        if "onnxruntime" in package:
            example_file.write_text('''/**
 * ONNX Runtime Web Usage Example for FraudShield Uganda
 *
 * Installation: npm install onnxruntime-web
 */

// Browser usage (via script tag or bundler)
// <script src="https://cdn.jsdelivr.net/npm/onnxruntime-web/dist/ort.min.js"></script>

async function runFraudDetection() {
    // Load model
    const session = await ort.InferenceSession.create('fraud_model.onnx', {
        executionProviders: ['wasm']  // or 'webgpu' for GPU
    });

    // Prepare features (15 transaction features)
    const features = new Float32Array([
        500000,   // amount
        1.2,      // amount ratio
        14,       // hour
        2,        // day of week
        0,        // is weekend
        0,        // after hours
        365,      // customer age
        15,       // tx count 30d
        400000,   // avg amount 30d
        0.2,      // merchant category
        1,        // same device
        0,        // distance
        60,       // minutes since prev
        0,        // failed attempts
        5,        // unique merchants
    ]);

    const input = new ort.Tensor('float32', features, [1, 15]);
    const results = await session.run({ input: input });

    const fraudScore = results.output.data[0];
    console.log('Fraud Score:', fraudScore);

    return fraudScore > 0.5 ? 'FRAUD' : 'LEGITIMATE';
}
''')
        elif "tensorflow" in package:
            example_file.write_text('''/**
 * TensorFlow.js WebGPU Usage Example for FraudShield Uganda
 *
 * Installation: npm install @tensorflow/tfjs @tensorflow/tfjs-backend-webgpu
 */

import * as tf from '@tensorflow/tfjs';
import '@tensorflow/tfjs-backend-webgpu';

async function runFraudDetection() {
    // Use WebGPU backend (3x faster than WebGL)
    await tf.setBackend('webgpu');

    // Load model
    const model = await tf.loadLayersModel('fraud_model/model.json');

    // Prepare input
    const features = tf.tensor2d([[
        500000, 1.2, 14, 2, 0, 0, 365, 15, 400000, 0.2, 1, 0, 60, 0, 5
    ]]);

    // Run prediction
    const prediction = model.predict(features);
    const fraudScore = prediction.dataSync()[0];

    console.log('Fraud Score:', fraudScore);
    return fraudScore > 0.5 ? 'FRAUD' : 'LEGITIMATE';
}
''')

        print(f"  Created usage example: {example_file}")
        print(f"  Note: Run 'npm install {package}' in your project directory")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def download_cargo(model_info: dict, target_dir: Path) -> bool:
    """Create Cargo.toml and usage example for Rust crate."""
    try:
        package = model_info["package"]
        print(f"  Cargo Crate: {package}")
        print(f"  Add to Cargo.toml: {package} = \"*\"")

        # Create usage example
        ensure_dir(target_dir)

        # Create Cargo.toml
        cargo_file = target_dir / "Cargo.toml"
        cargo_file.write_text(f'''[package]
name = "fraudshield-{package.replace("-", "_")}"
version = "0.1.0"
edition = "2021"

[dependencies]
{package} = "*"

# For WASM compilation
[lib]
crate-type = ["cdylib", "rlib"]

[target.'cfg(target_arch = "wasm32")'.dependencies]
wasm-bindgen = "0.2"
''')

        # Create usage example
        example_file = target_dir / "src" / "lib.rs"
        ensure_dir(target_dir / "src")

        if "isolation" in package.lower():
            example_file.write_text('''//! Extended Isolation Forest for FraudShield Uganda
//!
//! Compile to WASM: cargo build --target wasm32-unknown-unknown --release

use extended_isolation_forest::{Forest, ForestOptions};

pub fn detect_fraud(transaction_features: &[f64]) -> f64 {
    // Training data (in production, load pre-trained model)
    let training_data: Vec<Vec<f64>> = vec![
        // Normal transactions
        vec![100000.0, 1.0, 10.0, 1.0, 0.0],
        vec![200000.0, 1.2, 14.0, 3.0, 0.0],
        // ... more training data
    ];

    let options = ForestOptions {
        n_trees: 150,
        sample_size: 200,
        max_tree_depth: None,
        extension_level: 1,
    };

    let forest = Forest::from_slice(
        training_data.iter().map(|v| v.as_slice()).collect::<Vec<_>>().as_slice(),
        &options
    ).expect("Failed to build forest");

    // Score new transaction (higher = more anomalous)
    forest.score(transaction_features)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_fraud_detection() {
        let normal_tx = [150000.0, 1.1, 12.0, 2.0, 0.0];
        let suspicious_tx = [5000000.0, 10.0, 23.0, 6.0, 1.0];

        let normal_score = detect_fraud(&normal_tx);
        let suspicious_score = detect_fraud(&suspicious_tx);

        // Suspicious should have higher anomaly score
        assert!(suspicious_score > normal_score);
    }
}
''')
        elif "smartcore" in package.lower():
            example_file.write_text('''//! smartcore Random Forest for FraudShield Uganda
//!
//! Compile to WASM: cargo build --target wasm32-wasi --release

use smartcore::ensemble::random_forest_classifier::RandomForestClassifier;
use smartcore::linalg::basic::matrix::DenseMatrix;

pub fn train_and_predict(
    training_features: Vec<Vec<f64>>,
    training_labels: Vec<u32>,
    new_transaction: Vec<f64>,
) -> u32 {
    // Convert to DenseMatrix
    let x = DenseMatrix::from_2d_vec(&training_features);
    let y = training_labels;

    // Train Random Forest
    let model = RandomForestClassifier::fit(
        &x, &y, Default::default()
    ).expect("Failed to train model");

    // Predict on new transaction
    let x_new = DenseMatrix::from_2d_vec(&vec![new_transaction]);
    let predictions = model.predict(&x_new).expect("Prediction failed");

    predictions[0]  // 0 = legitimate, 1 = fraud
}
''')
        else:
            example_file.write_text(f'''//! {package} for FraudShield Uganda
//!
//! Compile to WASM: cargo build --target wasm32-unknown-unknown --release

// Add your implementation here
// See crate documentation: https://crates.io/crates/{package}
''')

        print(f"  Created Cargo.toml and example: {target_dir}")
        print(f"  To compile to WASM: cd {target_dir} && cargo build --target wasm32-unknown-unknown --release")
        return True
    except Exception as e:
        print(f"  Error: {e}")
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
    elif source == "npm":
        return download_npm(model_info, target_dir)
    elif source == "cargo":
        return download_cargo(model_info, target_dir)
    else:
        print(f"  Unknown source type: {source}")
        return False


def list_models() -> None:
    """List all available models."""
    print("\nAvailable Models for FraudShield Uganda:")
    print("=" * 60)

    # Separate server-side and browser/WASM models
    server_models = {k: v for k, v in MODELS.items() if not v.get("wasm_compatible")}
    wasm_models = {k: v for k, v in MODELS.items() if v.get("wasm_compatible")}

    print("\n--- Server-Side Models ---")
    for key, info in server_models.items():
        status = "Downloaded" if (MODELS_DIR / key).exists() else "Not downloaded"
        print(f"\n  {key}")
        print(f"    Name: {info['name']}")
        print(f"    Description: {info['description']}")
        print(f"    Size: {info['size']}")
        print(f"    Status: [{status}]")

    print("\n--- Browser/WASM Models ---")
    for key, info in wasm_models.items():
        status = "Downloaded" if (MODELS_DIR / key).exists() else "Not downloaded"
        print(f"\n  {key}")
        print(f"    Name: {info['name']}")
        print(f"    Description: {info['description']}")
        print(f"    Size: {info['size']}")
        print(f"    Source: {info['source']}")
        if info.get("input_shape"):
            print(f"    Input Shape: {info['input_shape']}")
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

    reqs = info.get('requirements', [])
    if reqs:
        print(f"Requirements: {', '.join(reqs)}")

    if info["source"] == "huggingface":
        print(f"HuggingFace Repo: {info['repo_id']}")
    elif info["source"] == "github":
        print(f"GitHub URL: {info['repo_url']}")
    elif info["source"] == "pypi":
        print(f"PyPI Package: {info['package']}")
    elif info["source"] == "npm":
        print(f"NPM Package: {info['package']}")
    elif info["source"] == "cargo":
        print(f"Cargo Crate: {info['package']}")

    # WASM/Browser info
    if info.get("wasm_compatible"):
        print("\n--- Browser/WASM Info ---")
        print("WASM Compatible: Yes")
        if info.get("input_shape"):
            print(f"Input Shape: {info['input_shape']}")
        if info.get("note"):
            print(f"Note: {info['note']}")

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
