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

- `integrations/huggingface_integration.py` - HuggingFace model integration
- `integrations/autoencoder_integration.py` - Keras autoencoder integration
- `integrations/ensemble_integration.py` - Combining multiple models

## Model Selection Guide

| Scenario | Recommended Model | Reason |
|----------|-------------------|--------|
| General fraud detection | HuggingFace Fraud-detection | Pre-trained, high accuracy |
| No labeled data | Keras Autoencoder | Unsupervised learning |
| Time-series transactions | IBM ONNX LSTM | Captures temporal patterns |
| Fast inference needed | PyOD Isolation Forest | Lightweight, fast |
| High interpretability | XGBoost/LightGBM | Feature importance |
| Complete platform | Tazama | Full infrastructure |

## Hardware Requirements

| Model Type | RAM | GPU | Disk |
|------------|-----|-----|------|
| HuggingFace Transformers | 8GB+ | Optional (faster) | 2GB |
| Keras Autoencoder | 4GB | Optional | 500MB |
| PyOD Models | 2GB | Not needed | 100MB |
| XGBoost/LightGBM | 4GB | Not needed | 200MB |

## License Information

| Model | License |
|-------|---------|
| HuggingFace models | Apache 2.0 |
| Keras Autoencoder | MIT |
| IBM ONNX | Apache 2.0 |
| Tazama | Apache 2.0 |
| PyOD | BSD 2-Clause |

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
