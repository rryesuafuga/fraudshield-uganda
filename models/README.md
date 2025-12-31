# FraudShield Uganda - ML Models Repository

This folder contains documentation and scripts for downloading open-source fraud detection machine learning models. Models are downloaded on-demand to avoid storing large binary files in Git.

## Available Models

### 1. HuggingFace Models (vaibhav07112004)

**Repository**: [vaibhav07112004 on HuggingFace](https://huggingface.co/vaibhav07112004)

| Model | Type | Use Case | Size |
|-------|------|----------|------|
| `Fraud-detection` | Binary Classification | General fraud detection | ~500MB |
| `Credit_card_fraud_detection` | Binary Classification | Credit card transactions | ~450MB |

**Features**:
- Pre-trained on financial transaction data
- High accuracy on imbalanced datasets
- Ready for fine-tuning

### 2. Keras Autoencoders (esenthil)

**Repository**: [GitHub - esenthil/fraud_detection](https://github.com/esenthil/fraud_detection)

| Model | Architecture | Use Case |
|-------|--------------|----------|
| Autoencoder | Deep Neural Network | Anomaly detection via reconstruction error |

**Features**:
- Unsupervised learning approach
- No labeled data required
- Good for detecting novel fraud patterns
- Lightweight and fast inference

### 3. IBM ONNX LSTM Models

**Repository**: [onnx/models - IBM Watson](https://github.com/onnx/models)

| Model | Architecture | Use Case |
|-------|--------------|----------|
| LSTM Classifier | Recurrent Neural Network | Sequential transaction analysis |

**Features**:
- ONNX format for cross-platform deployment
- Optimized for time-series data
- Captures temporal patterns in transactions

### 4. Tazama Platform (Open Source)

**Repository**: [GitHub - tazama-lf/tazama](https://github.com/tazama-lf/tazama)

**Description**: Complete open-source platform for real-time fraud monitoring in financial services.

**Components**:
- Rule engine for pattern detection
- ML models for anomaly scoring
- Real-time transaction processing
- Dashboard and alerting

**Best For**: Organizations wanting a complete fraud detection infrastructure.

### 5. PyOD Anomaly Detection

**Repository**: [yzhao062/pyod](https://github.com/yzhao062/pyod)

**Pre-trained models available**:
- Isolation Forest
- Local Outlier Factor (LOF)
- One-Class SVM
- AutoEncoder variants

**Features**:
- 40+ anomaly detection algorithms
- Scikit-learn compatible API
- Easy integration with existing pipelines

### 6. XGBoost/LightGBM Pre-trained Models

**Sources**:
- [Kaggle Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
- Various GitHub repositories

**Features**:
- Gradient boosting models
- High performance on tabular data
- Fast inference time
- Interpretable feature importance

---

## Browser-Based ML (WebAssembly & WebGPU)

These models run directly in the browser without server round-trips, enabling offline-capable fraud detection.

### 7. IBM ai-on-z-fraud-detection (ONNX)

**Repository**: [github.com/IBM/ai-on-z-fraud-detection](https://github.com/IBM/ai-on-z-fraud-detection)

| Model | Architecture | Input Shape | License |
|-------|--------------|-------------|---------|
| LSTM Fraud | 2-layer LSTM (200 units) | (7, 16, 220) | Apache 2.0 |
| GRU Fraud | 2-layer GRU (200 units) | (7, 16, 220) | Apache 2.0 |

**Features**:
- Pre-converted to ONNX format via tf2onnx
- Trained on IBM TabFormer credit card data
- Analyzes sequences of 7 transactions
- Loads directly into ONNX Runtime Web

### 8. Hazelcast fraud-detection-onnx (LightGBM)

**Repository**: [github.com/hazelcast/fraud-detection-onnx](https://github.com/hazelcast/fraud-detection-onnx)

| Model | Type | Features | Inference Time |
|-------|------|----------|----------------|
| LightGBM ONNX | Gradient Boosting | 15 features | <0.1ms |

**Features**:
- Already exported to ONNX format
- Sub-millisecond inference per transaction
- Complete feature engineering pipeline documented
- Ideal for real-time browser-based detection

### 9. Vaibhav Singh Fraud Models (HuggingFace)

**Repository**: [huggingface.co/vaibhav07112004/fraud-detection-models](https://huggingface.co/vaibhav07112004/fraud-detection-models)

| Model | Accuracy | Use Case |
|-------|----------|----------|
| Credit Card Fraud | 99.1% | Card transactions |
| QR Fraud | ~95% | Mobile payments |
| E-commerce Fraud | ~95% | Online purchases |
| APP Fraud | ~95% | Application fraud |
| Synthetic Identity | ~95% | Fake identities |

**Features**:
- 11 specialized fraud models (MIT License)
- Ensemble achieves 95.7% overall accuracy
- Requires sklearn-onnx conversion for WASM deployment

---

## WASM/WebGPU Inference Engines

### ONNX Runtime Web (Recommended)

**Repository**: [github.com/microsoft/onnxruntime](https://github.com/microsoft/onnxruntime)

```javascript
import * as ort from 'onnxruntime-web';
const session = await ort.InferenceSession.create('fraud_model.onnx', {
  executionProviders: ['wasm']  // or 'webgpu' for GPU acceleration
});
const input = new ort.Tensor('float32', transactionFeatures, [1, 15]);
const results = await session.run({ input: input });
```

**Features**:
- MIT License
- 4 execution providers: WASM, WebGL, WebGPU, WebNN
- 10x faster with SIMD and multithreading
- Best ONNX operator coverage

### tract (Rust → WASM)

**Repository**: [github.com/sonos/tract](https://github.com/sonos/tract)

**Features**:
- Pure Rust, compiles to WebAssembly natively
- 2,700+ GitHub stars, 85% ONNX test coverage
- MIT + Apache 2.0 dual license
- MobileNet in 70μs on Raspberry Pi Zero

### candle (Hugging Face Rust)

**Repository**: [github.com/huggingface/candle](https://github.com/huggingface/candle)

**Features**:
- 17,000+ stars, first-class WASM support
- `candle-wasm-examples/` for browser inference
- Loads weights from Hugging Face Hub
- ~120ms transformer latency in browser

### burn (Rust WebGPU)

**Repository**: [github.com/tracel-ai/burn](https://github.com/tracel-ai/burn)

**Features**:
- Native WebGPU via WGPU backend
- Compiles to ~2MB .wasm
- Automatic kernel fusion
- ONNX import to native Rust

### TensorFlow.js WebGPU

**Repository**: [github.com/tensorflow/tfjs](https://github.com/tensorflow/tfjs)

```javascript
import * as tf from '@tensorflow/tfjs';
import '@tensorflow/tfjs-backend-webgpu';
await tf.setBackend('webgpu');
const model = await tf.loadLayersModel('fraud_autoencoder/model.json');
```

**Features**:
- Apache 2.0 License
- 3x performance gain over WebGL
- Chrome 113+ support
- Autoencoders for anomaly detection

---

## Rust ML Crates for WASM

### smartcore

**Crate**: [crates.io/crates/smartcore](https://crates.io/crates/smartcore)

```rust
use smartcore::ensemble::random_forest_classifier::RandomForestClassifier;
let model = RandomForestClassifier::fit(&features, &fraud_labels, Default::default())?;
let predictions = model.predict(&new_transactions)?;
```

- WASM/WASI-first design
- Random Forests, SVM, Decision Trees, KNN, DBSCAN
- Apache 2.0 / MIT dual license

### linfa

**Repository**: [github.com/rust-ml/linfa](https://github.com/rust-ml/linfa)

- 3,400+ stars, scikit-learn alternative
- No BLAS dependency for WASM compilation
- linfa-trees, linfa-clustering, linfa-svm, linfa-bayes

### Extended Isolation Forest

**Crate**: [crates.io/crates/extended-isolation-forest](https://crates.io/crates/extended-isolation-forest)

```rust
use extended_isolation_forest::{Forest, ForestOptions};
let options = ForestOptions { n_trees: 150, sample_size: 200, extension_level: 1, .. };
let forest = Forest::from_slice(&transactions, &options)?;
let fraud_score = forest.score(&new_transaction);  // >0.5 = anomaly
```

---

## Performance Comparison

| Framework | Latency | Model Size Limit | GPU | Browser Support |
|-----------|---------|------------------|-----|-----------------|
| ONNX Runtime Web (WASM) | 10-100ms | Unlimited | WebGPU/WebGL | 95%+ |
| ONNX Runtime Web (WebGPU) | 2-20ms | 4GB | Native | ~70% |
| tract (WASM) | ~70μs (small) | Unlimited | No | 95%+ |
| candle (WASM) | ~120ms | Browser memory | WebGPU | 95%+ |
| TensorFlow.js WASM | 3-11x faster than JS | Limited | WebGL | 95%+ |

**WebGPU Support** (Late 2025): Chrome/Edge 113+, Safari 18+, Chrome Android 121+, Firefox 141+ (Windows flag)

---

## Quick Start

### Download All Models
```bash
python download_models.py --all
```

### Download Specific Model
```bash
python download_models.py --model huggingface-fraud
python download_models.py --model keras-autoencoder
python download_models.py --model pyod-isolation-forest
```

### List Available Models
```bash
python download_models.py --list
```

## Integration with FraudShield

See the `integrations/` folder for examples of how to use these models with FraudShield Uganda:

**Server-Side (Python):**
- `integrations/huggingface_integration.py` - HuggingFace model integration
- `integrations/autoencoder_integration.py` - Keras autoencoder integration
- `integrations/ensemble_integration.py` - Combining multiple models

**Browser-Side (WASM/WebGPU):**
- `wasm/browser_integration.html` - Complete browser demo
- `wasm/onnx_runtime_example.js` - ONNX Runtime Web usage
- `wasm/feature_extraction.js` - Feature engineering for fraud models

## Model Selection Guide

| Scenario | Recommended Model | Reason |
|----------|-------------------|--------|
| General fraud detection | HuggingFace Fraud-detection | Pre-trained, high accuracy |
| No labeled data | Keras Autoencoder | Unsupervised learning |
| Time-series transactions | IBM ONNX LSTM | Captures temporal patterns |
| Fast inference needed | PyOD Isolation Forest | Lightweight, fast |
| High interpretability | XGBoost/LightGBM | Feature importance |
| Complete platform | Tazama | Full infrastructure |
| **Browser-based (offline)** | Hazelcast ONNX + ORT Web | Sub-ms inference, no server |
| **Browser + GPU** | ONNX Runtime WebGPU | 2-20ms with GPU acceleration |
| **Rust/WASM edge** | tract + Extended Isolation Forest | Pure Rust, tiny footprint |

## Hardware Requirements

| Model Type | RAM | GPU | Disk |
|------------|-----|-----|------|
| HuggingFace Transformers | 8GB+ | Optional (faster) | 2GB |
| Keras Autoencoder | 4GB | Optional | 500MB |
| PyOD Models | 2GB | Not needed | 100MB |
| XGBoost/LightGBM | 4GB | Not needed | 200MB |
| **Browser WASM** | Browser memory | WebGPU optional | <50MB |
| **Browser WebGPU** | Browser memory | Required | <100MB |

## License Information

| Model/Framework | License | Commercial Use |
|-----------------|---------|----------------|
| HuggingFace models | Apache 2.0 | ✅ Permitted |
| Keras Autoencoder | MIT | ✅ Permitted |
| IBM ONNX | Apache 2.0 | ✅ Permitted |
| Tazama | Apache 2.0 | ✅ Permitted |
| PyOD | BSD 2-Clause | ✅ Permitted |
| Hazelcast ONNX | Apache 2.0 | ✅ Permitted |
| Vaibhav Singh models | MIT | ✅ Permitted |
| ONNX Runtime Web | MIT | ✅ Permitted |
| tract | MIT + Apache 2.0 | ✅ Permitted |
| candle | MIT + Apache 2.0 | ✅ Permitted |
| burn | MIT + Apache 2.0 | ✅ Permitted |
| smartcore | MIT + Apache 2.0 | ✅ Permitted |
| linfa | MIT + Apache 2.0 | ✅ Permitted |
| TensorFlow.js | Apache 2.0 | ✅ Permitted |

## Contributing

To add new models:
1. Add model information to this README
2. Update `download_models.py` with download logic
3. Create integration example in `integrations/`
4. Submit a pull request

## Support

- **Email**: sseguya256@gmail.com
- **Website**: [fraudshield-uganda.vercel.app](https://fraudshield-uganda.vercel.app)

---

*Note: Model files are not stored in this repository. Use the download script to fetch models as needed.*
