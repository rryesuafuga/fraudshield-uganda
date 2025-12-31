"""
Ensemble Model Integration for FraudShield Uganda

This module combines multiple ML models for more robust fraud detection.
Ensemble methods typically outperform individual models by reducing variance
and capturing different aspects of fraudulent behavior.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Available model types."""
    ISOLATION_FOREST = "isolation_forest"
    AUTOENCODER = "autoencoder"
    HUGGINGFACE = "huggingface"
    LOCAL_OUTLIER = "local_outlier"
    ONE_CLASS_SVM = "one_class_svm"


@dataclass
class ModelWeight:
    """Weight configuration for a model in the ensemble."""
    model_type: ModelType
    weight: float
    enabled: bool = True


class FraudEnsemble:
    """
    Ensemble fraud detection combining multiple models.

    Supports:
    - Isolation Forest (fast, good for tabular data)
    - Autoencoder (unsupervised anomaly detection)
    - HuggingFace Transformer (pre-trained on fraud data)
    - Local Outlier Factor (density-based)
    - One-Class SVM (boundary-based)
    """

    DEFAULT_WEIGHTS = {
        ModelType.ISOLATION_FOREST: 0.25,
        ModelType.AUTOENCODER: 0.25,
        ModelType.HUGGINGFACE: 0.30,
        ModelType.LOCAL_OUTLIER: 0.10,
        ModelType.ONE_CLASS_SVM: 0.10,
    }

    def __init__(
        self,
        models: Optional[List[ModelType]] = None,
        weights: Optional[Dict[ModelType, float]] = None,
    ):
        """
        Initialize the ensemble.

        Args:
            models: List of model types to use (default: all available)
            weights: Custom weights for each model
        """
        self.models = models or list(ModelType)
        self.weights = weights or self.DEFAULT_WEIGHTS
        self._initialized_models: Dict[ModelType, Any] = {}
        self._available_models: List[ModelType] = []

    def initialize(self) -> bool:
        """Initialize all available models."""
        for model_type in self.models:
            try:
                if model_type == ModelType.ISOLATION_FOREST:
                    self._init_isolation_forest()
                elif model_type == ModelType.LOCAL_OUTLIER:
                    self._init_local_outlier()
                elif model_type == ModelType.ONE_CLASS_SVM:
                    self._init_one_class_svm()
                elif model_type == ModelType.AUTOENCODER:
                    self._init_autoencoder()
                elif model_type == ModelType.HUGGINGFACE:
                    self._init_huggingface()

                self._available_models.append(model_type)
                logger.info(f"Initialized: {model_type.value}")

            except ImportError as e:
                logger.warning(f"Skipping {model_type.value}: {e}")
            except Exception as e:
                logger.warning(f"Failed to init {model_type.value}: {e}")

        if not self._available_models:
            logger.error("No models available!")
            return False

        logger.info(f"Ensemble ready with {len(self._available_models)} models")
        return True

    def _init_isolation_forest(self):
        """Initialize Isolation Forest model."""
        from pyod.models.iforest import IForest
        self._initialized_models[ModelType.ISOLATION_FOREST] = IForest(
            contamination=0.1,
            random_state=42,
        )

    def _init_local_outlier(self):
        """Initialize Local Outlier Factor model."""
        from pyod.models.lof import LOF
        self._initialized_models[ModelType.LOCAL_OUTLIER] = LOF(
            n_neighbors=20,
            contamination=0.1,
        )

    def _init_one_class_svm(self):
        """Initialize One-Class SVM model."""
        from pyod.models.ocsvm import OCSVM
        self._initialized_models[ModelType.ONE_CLASS_SVM] = OCSVM(
            contamination=0.1,
        )

    def _init_autoencoder(self):
        """Initialize Autoencoder model."""
        from .autoencoder_integration import AutoencoderAnomalyDetector
        self._initialized_models[ModelType.AUTOENCODER] = (
            AutoencoderAnomalyDetector()
        )

    def _init_huggingface(self):
        """Initialize HuggingFace model."""
        from .huggingface_integration import HuggingFacePredictor
        self._initialized_models[ModelType.HUGGINGFACE] = HuggingFacePredictor()

    def extract_features(self, transaction: Dict[str, Any]) -> List[float]:
        """
        Extract numerical features from a transaction for PyOD models.

        Args:
            transaction: Transaction dictionary

        Returns:
            List of numerical features
        """
        import re
        from datetime import datetime

        features = []

        # Amount
        amount = float(transaction.get("amount", 0))
        features.append(amount)

        # Time features
        time_str = str(transaction.get("approval_time", "12:00"))
        try:
            match = re.match(r"(\d+):(\d+)", time_str)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2))
            else:
                hour, minute = 12, 0
        except (ValueError, AttributeError):
            hour, minute = 12, 0

        features.append(hour)
        features.append(minute)
        features.append(1 if (hour < 8 or hour > 18) else 0)  # After hours

        # Date features
        date_str = str(transaction.get("loan_date", ""))[:10]
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            features.append(date.weekday())
            features.append(date.month)
            features.append(1 if date.weekday() >= 5 else 0)  # Weekend
        except ValueError:
            features.extend([2, 6, 0])

        return features

    def fit(self, transactions: List[Dict[str, Any]]) -> bool:
        """
        Train the ensemble on historical transactions.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            True if training succeeded
        """
        import numpy as np

        if not self._initialized_models:
            if not self.initialize():
                return False

        # Extract features for PyOD models
        X = np.array([self.extract_features(t) for t in transactions])

        # Train each model
        for model_type in self._available_models:
            try:
                model = self._initialized_models[model_type]

                if model_type in [
                    ModelType.ISOLATION_FOREST,
                    ModelType.LOCAL_OUTLIER,
                    ModelType.ONE_CLASS_SVM,
                ]:
                    model.fit(X)
                    logger.info(f"Trained {model_type.value}")

                elif model_type == ModelType.AUTOENCODER:
                    model.fit(transactions)
                    logger.info(f"Trained {model_type.value}")

                # HuggingFace is pre-trained, no fitting needed

            except Exception as e:
                logger.warning(f"Failed to train {model_type.value}: {e}")

        return True

    def predict(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get ensemble fraud prediction for a transaction.

        Args:
            transaction: Transaction dictionary

        Returns:
            Dictionary with scores from each model and final ensemble score
        """
        import numpy as np

        if not self._available_models:
            if not self.initialize():
                raise RuntimeError("No models available")

        scores: Dict[str, float] = {}
        X = np.array([self.extract_features(transaction)])

        for model_type in self._available_models:
            try:
                model = self._initialized_models[model_type]

                if model_type in [
                    ModelType.ISOLATION_FOREST,
                    ModelType.LOCAL_OUTLIER,
                    ModelType.ONE_CLASS_SVM,
                ]:
                    # PyOD models return decision scores
                    raw_score = model.decision_function(X)[0]
                    # Normalize to 0-1 using sigmoid
                    score = 1 / (1 + np.exp(-raw_score))
                    scores[model_type.value] = score

                elif model_type == ModelType.AUTOENCODER:
                    score, _ = model.predict(transaction)
                    scores[model_type.value] = score

                elif model_type == ModelType.HUGGINGFACE:
                    score = model.predict(transaction)
                    scores[model_type.value] = score

            except Exception as e:
                logger.warning(f"Prediction failed for {model_type.value}: {e}")

        # Calculate weighted ensemble score
        total_weight = 0
        weighted_sum = 0

        for model_type in self._available_models:
            model_key = model_type.value
            if model_key in scores:
                weight = self.weights.get(model_type, 0.2)
                weighted_sum += scores[model_key] * weight
                total_weight += weight

        ensemble_score = weighted_sum / total_weight if total_weight > 0 else 0.5

        return {
            "ensemble_score": ensemble_score,
            "risk_level": self._get_risk_level(ensemble_score),
            "model_scores": scores,
            "models_used": len(scores),
        }

    def _get_risk_level(self, score: float) -> str:
        """Convert score to risk level."""
        if score >= 0.7:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"

    def predict_batch(
        self, transactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Get predictions for multiple transactions.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            List of prediction results
        """
        return [self.predict(t) for t in transactions]


def integrate_with_fraudshield_api(ensemble: FraudEnsemble):
    """
    Example FastAPI integration for FraudShield backend.
    """

    async def analyze_with_ml(loan_data: List[Dict]) -> Dict:
        """
        Enhanced analysis endpoint combining rules + ML.
        """
        # Get ML predictions
        ml_results = ensemble.predict_batch(loan_data)

        # Combine with rules-based alerts
        high_risk_loans = [
            {
                **loan,
                "ml_score": result["ensemble_score"],
                "ml_risk": result["risk_level"],
            }
            for loan, result in zip(loan_data, ml_results)
            if result["ensemble_score"] > 0.5
        ]

        return {
            "total_loans": len(loan_data),
            "ml_flagged": len(high_risk_loans),
            "high_risk_loans": high_risk_loans,
            "models_used": ml_results[0]["models_used"] if ml_results else 0,
        }

    return analyze_with_ml


# Example usage
if __name__ == "__main__":
    print("FraudShield Ensemble Example")
    print("=" * 50)

    # Create ensemble with available models
    ensemble = FraudEnsemble(
        models=[
            ModelType.ISOLATION_FOREST,
            # Add more as needed
        ]
    )

    print("\nInitializing models...")
    if ensemble.initialize():
        # Generate sample training data
        import random

        training_data = []
        for _ in range(500):
            training_data.append({
                "amount": random.randint(100000, 5000000),
                "approval_time": f"{random.randint(8, 17)}:{random.randint(0, 59):02d}",
                "loan_date": f"2025-01-{random.randint(1, 28):02d}",
            })

        print("Training ensemble...")
        ensemble.fit(training_data)

        # Test prediction
        test_transaction = {
            "amount": 50000000,  # Very large amount
            "approval_time": "23:45",  # Late night
            "loan_date": "2025-01-15",
        }

        print("\nTest Transaction:")
        print(f"  Amount: {test_transaction['amount']:,} UGX")
        print(f"  Time: {test_transaction['approval_time']}")
        print(f"  Date: {test_transaction['loan_date']}")

        result = ensemble.predict(test_transaction)

        print("\nPrediction Results:")
        print(f"  Ensemble Score: {result['ensemble_score']:.2%}")
        print(f"  Risk Level: {result['risk_level']}")
        print(f"  Models Used: {result['models_used']}")

        if result["model_scores"]:
            print("\n  Individual Model Scores:")
            for model, score in result["model_scores"].items():
                print(f"    - {model}: {score:.2%}")
    else:
        print("Failed to initialize ensemble.")
        print("Install dependencies: pip install pyod")
