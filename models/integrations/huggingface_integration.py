"""
HuggingFace Model Integration for FraudShield Uganda

This module provides integration with HuggingFace fraud detection models.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class HuggingFacePredictor:
    """
    Wrapper for HuggingFace fraud detection models.

    Supports:
    - vaibhav07112004/Fraud-detection
    - vaibhav07112004/Credit_card_fraud_detection
    """

    def __init__(
        self,
        model_name: str = "vaibhav07112004/Fraud-detection",
        device: str = "auto",
    ):
        """
        Initialize the HuggingFace predictor.

        Args:
            model_name: HuggingFace model identifier
            device: Device to use ('cpu', 'cuda', or 'auto')
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = device
        self._initialized = False

    def initialize(self) -> bool:
        """Load the model and tokenizer."""
        try:
            from transformers import (
                AutoModelForSequenceClassification,
                AutoTokenizer,
            )
            import torch

            logger.info(f"Loading model: {self.model_name}")

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name
            )

            # Set device
            if self.device == "auto":
                self.device = "cuda" if torch.cuda.is_available() else "cpu"

            self.model.to(self.device)
            self.model.eval()

            self._initialized = True
            logger.info(f"Model loaded successfully on {self.device}")
            return True

        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            logger.error("Install with: pip install transformers torch")
            return False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def transaction_to_text(self, transaction: Dict[str, Any]) -> str:
        """
        Convert a transaction dictionary to text for model input.

        Args:
            transaction: Dictionary with transaction details

        Returns:
            Text description of the transaction
        """
        parts = []

        if "amount" in transaction:
            parts.append(f"Amount: {transaction['amount']} UGX")

        if "borrower_name" in transaction:
            parts.append(f"Borrower: {transaction['borrower_name']}")

        if "officer_id" in transaction:
            parts.append(f"Officer: {transaction['officer_id']}")

        if "loan_date" in transaction:
            parts.append(f"Date: {transaction['loan_date']}")

        if "approval_time" in transaction:
            parts.append(f"Time: {transaction['approval_time']}")

        if "branch" in transaction:
            parts.append(f"Branch: {transaction['branch']}")

        if "status" in transaction:
            parts.append(f"Status: {transaction['status']}")

        return " | ".join(parts) if parts else str(transaction)

    def predict(self, transaction: Dict[str, Any]) -> float:
        """
        Predict fraud probability for a single transaction.

        Args:
            transaction: Dictionary with transaction details

        Returns:
            Fraud probability between 0 and 1
        """
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("Failed to initialize model")

        import torch

        text = self.transaction_to_text(transaction)

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.softmax(outputs.logits, dim=-1)
            fraud_probability = predictions[0][1].item()

        return fraud_probability

    def predict_batch(
        self, transactions: List[Dict[str, Any]], batch_size: int = 32
    ) -> List[float]:
        """
        Predict fraud probabilities for multiple transactions.

        Args:
            transactions: List of transaction dictionaries
            batch_size: Number of transactions to process at once

        Returns:
            List of fraud probabilities
        """
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("Failed to initialize model")

        import torch

        texts = [self.transaction_to_text(t) for t in transactions]
        all_probabilities = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]

            inputs = self.tokenizer(
                batch_texts,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True,
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.softmax(outputs.logits, dim=-1)
                probabilities = predictions[:, 1].tolist()
                all_probabilities.extend(probabilities)

        return all_probabilities


def integrate_with_fraudshield(predictor: HuggingFacePredictor):
    """
    Example of integrating with FraudShield Uganda backend.

    This function shows how to add ML predictions to the existing
    rules-based fraud detection system.
    """
    # Example integration with FraudShield analysis pipeline
    def enhanced_fraud_analysis(loan_data: List[Dict]) -> List[Dict]:
        """
        Enhance loan analysis with ML predictions.
        """
        # Get ML predictions
        ml_scores = predictor.predict_batch(loan_data)

        # Combine with existing analysis
        for i, loan in enumerate(loan_data):
            loan["ml_fraud_score"] = ml_scores[i]
            loan["ml_risk_level"] = (
                "HIGH" if ml_scores[i] > 0.7 else
                "MEDIUM" if ml_scores[i] > 0.4 else
                "LOW"
            )

        return loan_data

    return enhanced_fraud_analysis


# Example usage
if __name__ == "__main__":
    # Initialize predictor
    predictor = HuggingFacePredictor()

    # Test transaction
    test_transaction = {
        "amount": 5000000,
        "borrower_name": "John Doe",
        "officer_id": "OFF001",
        "loan_date": "2025-01-15",
        "approval_time": "23:45",
        "branch": "Kampala Central",
        "status": "Approved",
    }

    try:
        score = predictor.predict(test_transaction)
        print(f"Fraud probability: {score:.2%}")
    except RuntimeError as e:
        print(f"Error: {e}")
        print("Make sure to install: pip install transformers torch")
