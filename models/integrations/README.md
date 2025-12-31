# FraudShield Integration Examples

This folder contains examples of how to integrate various ML models with FraudShield Uganda.

## Files

- `huggingface_integration.py` - Using HuggingFace transformer models
- `autoencoder_integration.py` - Anomaly detection with autoencoders
- `ensemble_integration.py` - Combining multiple models for better accuracy

## Quick Start

```python
from integrations.ensemble_integration import FraudEnsemble

# Initialize ensemble
ensemble = FraudEnsemble()

# Score a transaction
transaction = {
    "amount": 5000000,
    "borrower_id": "B001",
    "officer_id": "O001",
    "time": "23:45",
    "branch": "Kampala"
}

risk_score = ensemble.predict(transaction)
print(f"Risk Score: {risk_score:.2%}")
```

## Integration Architecture

```
                    ┌─────────────────┐
                    │  Raw Transaction │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Feature Extraction│
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
│  HuggingFace  │   │  Autoencoder  │   │  Isolation   │
│  Transformer  │   │   (Anomaly)   │   │   Forest     │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Ensemble Vote  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Risk Score    │
                    └─────────────────┘
```

## Model Selection

| Use Case | Recommended Integration |
|----------|------------------------|
| Real-time scoring | `huggingface_integration.py` |
| Batch processing | `autoencoder_integration.py` |
| Production system | `ensemble_integration.py` |
