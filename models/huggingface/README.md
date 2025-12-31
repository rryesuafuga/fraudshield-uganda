# HuggingFace Models Configuration

This folder contains configuration and usage examples for HuggingFace fraud detection models.

## Available Models

### 1. vaibhav07112004/Fraud-detection

General-purpose fraud detection model trained on financial transaction data.

**Model Card**: https://huggingface.co/vaibhav07112004/Fraud-detection

### 2. vaibhav07112004/Credit_card_fraud_detection

Specialized model for detecting credit card transaction fraud.

**Model Card**: https://huggingface.co/vaibhav07112004/Credit_card_fraud_detection

## Installation

```bash
pip install transformers torch huggingface_hub
```

## Usage

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# Load model
model_name = "vaibhav07112004/Fraud-detection"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Prepare input (example: transaction description)
text = "Wire transfer of $50,000 to offshore account"
inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

# Predict
with torch.no_grad():
    outputs = model(**inputs)
    predictions = torch.softmax(outputs.logits, dim=-1)
    fraud_probability = predictions[0][1].item()

print(f"Fraud probability: {fraud_probability:.2%}")
```

## Fine-tuning for Uganda Context

To fine-tune these models for Ugandan microfinance data:

```python
from transformers import Trainer, TrainingArguments
from datasets import Dataset

# Prepare your training data
train_data = [
    {"text": "Loan disbursement to multiple accounts same day", "label": 1},
    {"text": "Regular monthly loan payment", "label": 0},
    # Add more examples...
]

dataset = Dataset.from_list(train_data)

training_args = TrainingArguments(
    output_dir="./uganda-fraud-model",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    learning_rate=2e-5,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)

trainer.train()
```

## Memory Requirements

| Model | RAM | GPU Memory |
|-------|-----|------------|
| Fraud-detection | 4GB | 2GB (optional) |
| Credit_card_fraud | 4GB | 2GB (optional) |

## Notes

- Models work on CPU but are faster on GPU
- First run downloads model weights (~500MB each)
- Cached in `~/.cache/huggingface/`
