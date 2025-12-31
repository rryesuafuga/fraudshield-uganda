"""
Autoencoder Anomaly Detection Integration for FraudShield Uganda

This module provides anomaly detection using autoencoders.
Autoencoders learn to reconstruct normal transactions, and
high reconstruction error indicates potential fraud.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class AutoencoderAnomalyDetector:
    """
    Anomaly detection using autoencoder neural networks.

    The model learns to reconstruct normal transactions.
    Fraudulent transactions produce higher reconstruction errors.
    """

    def __init__(
        self,
        encoding_dim: int = 8,
        threshold_percentile: float = 95.0,
    ):
        """
        Initialize the autoencoder detector.

        Args:
            encoding_dim: Dimension of the encoded representation
            threshold_percentile: Percentile for anomaly threshold
        """
        self.encoding_dim = encoding_dim
        self.threshold_percentile = threshold_percentile
        self.model = None
        self.scaler = None
        self.threshold = None
        self._initialized = False
        self.feature_names = [
            "amount",
            "hour",
            "day_of_week",
            "month",
            "is_weekend",
            "amount_zscore",
        ]

    def _build_model(self, input_dim: int):
        """Build the autoencoder model."""
        try:
            from tensorflow import keras
            from tensorflow.keras import layers

            # Encoder
            inputs = keras.Input(shape=(input_dim,))
            x = layers.Dense(32, activation="relu")(inputs)
            x = layers.Dropout(0.2)(x)
            x = layers.Dense(16, activation="relu")(x)
            x = layers.Dropout(0.2)(x)
            encoded = layers.Dense(self.encoding_dim, activation="relu")(x)

            # Decoder
            x = layers.Dense(16, activation="relu")(encoded)
            x = layers.Dropout(0.2)(x)
            x = layers.Dense(32, activation="relu")(x)
            x = layers.Dropout(0.2)(x)
            decoded = layers.Dense(input_dim, activation="linear")(x)

            self.model = keras.Model(inputs, decoded)
            self.model.compile(optimizer="adam", loss="mse")

            logger.info(f"Built autoencoder with input_dim={input_dim}")
            return True

        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            logger.error("Install with: pip install tensorflow")
            return False

    def extract_features(self, transaction: Dict[str, Any]) -> np.ndarray:
        """
        Extract numerical features from a transaction.

        Args:
            transaction: Dictionary with transaction details

        Returns:
            Numpy array of features
        """
        from datetime import datetime

        features = []

        # Amount (normalized later)
        amount = float(transaction.get("amount", 0))
        features.append(amount)

        # Time-based features
        time_str = transaction.get("approval_time", "12:00")
        try:
            if ":" in str(time_str):
                parts = str(time_str).split(":")
                hour = int(parts[0])
            else:
                hour = 12
        except (ValueError, IndexError):
            hour = 12
        features.append(hour)

        # Date-based features
        date_str = transaction.get("loan_date", "")
        try:
            if date_str:
                date = datetime.strptime(str(date_str)[:10], "%Y-%m-%d")
                day_of_week = date.weekday()
                month = date.month
                is_weekend = 1 if day_of_week >= 5 else 0
            else:
                day_of_week = 2
                month = 6
                is_weekend = 0
        except (ValueError, TypeError):
            day_of_week = 2
            month = 6
            is_weekend = 0

        features.append(day_of_week)
        features.append(month)
        features.append(is_weekend)

        # Placeholder for z-score (calculated during batch processing)
        features.append(0)

        return np.array(features)

    def fit(
        self,
        transactions: List[Dict[str, Any]],
        epochs: int = 50,
        batch_size: int = 32,
    ) -> bool:
        """
        Train the autoencoder on normal transactions.

        Args:
            transactions: List of transaction dictionaries (assumed normal)
            epochs: Number of training epochs
            batch_size: Training batch size

        Returns:
            True if training succeeded
        """
        try:
            from sklearn.preprocessing import StandardScaler

            # Extract features
            X = np.array([self.extract_features(t) for t in transactions])

            # Calculate amount z-scores
            amounts = X[:, 0]
            amount_mean = np.mean(amounts)
            amount_std = np.std(amounts) + 1e-8
            X[:, -1] = (amounts - amount_mean) / amount_std

            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)

            # Build and train model
            if not self._build_model(X_scaled.shape[1]):
                return False

            self.model.fit(
                X_scaled,
                X_scaled,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=0.1,
                verbose=0,
            )

            # Calculate threshold from training data
            reconstructions = self.model.predict(X_scaled, verbose=0)
            mse = np.mean(np.square(X_scaled - reconstructions), axis=1)
            self.threshold = np.percentile(mse, self.threshold_percentile)

            self._initialized = True
            logger.info(f"Trained autoencoder, threshold={self.threshold:.4f}")
            return True

        except Exception as e:
            logger.error(f"Training error: {e}")
            return False

    def predict(self, transaction: Dict[str, Any]) -> Tuple[float, bool]:
        """
        Predict anomaly score for a transaction.

        Args:
            transaction: Dictionary with transaction details

        Returns:
            Tuple of (anomaly_score, is_anomaly)
        """
        if not self._initialized:
            raise RuntimeError("Model not trained. Call fit() first.")

        X = self.extract_features(transaction).reshape(1, -1)
        X_scaled = self.scaler.transform(X)

        reconstruction = self.model.predict(X_scaled, verbose=0)
        mse = np.mean(np.square(X_scaled - reconstruction))

        # Normalize to 0-1 range
        anomaly_score = min(mse / (self.threshold * 2), 1.0)
        is_anomaly = mse > self.threshold

        return anomaly_score, is_anomaly

    def predict_batch(
        self, transactions: List[Dict[str, Any]]
    ) -> List[Tuple[float, bool]]:
        """
        Predict anomaly scores for multiple transactions.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            List of (anomaly_score, is_anomaly) tuples
        """
        if not self._initialized:
            raise RuntimeError("Model not trained. Call fit() first.")

        X = np.array([self.extract_features(t) for t in transactions])

        # Calculate amount z-scores for batch
        amounts = X[:, 0]
        amount_mean = np.mean(amounts)
        amount_std = np.std(amounts) + 1e-8
        X[:, -1] = (amounts - amount_mean) / amount_std

        X_scaled = self.scaler.transform(X)
        reconstructions = self.model.predict(X_scaled, verbose=0)

        mse = np.mean(np.square(X_scaled - reconstructions), axis=1)

        results = []
        for m in mse:
            score = min(m / (self.threshold * 2), 1.0)
            is_anomaly = m > self.threshold
            results.append((score, is_anomaly))

        return results

    def save(self, path: str) -> None:
        """Save the trained model."""
        import pickle

        self.model.save(f"{path}_model.h5")
        with open(f"{path}_scaler.pkl", "wb") as f:
            pickle.dump(self.scaler, f)
        with open(f"{path}_threshold.pkl", "wb") as f:
            pickle.dump(self.threshold, f)

    def load(self, path: str) -> bool:
        """Load a trained model."""
        try:
            from tensorflow import keras
            import pickle

            self.model = keras.models.load_model(f"{path}_model.h5")
            with open(f"{path}_scaler.pkl", "rb") as f:
                self.scaler = pickle.load(f)
            with open(f"{path}_threshold.pkl", "rb") as f:
                self.threshold = pickle.load(f)

            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Generate sample training data (normal transactions)
    import random

    sample_transactions = []
    for i in range(1000):
        sample_transactions.append({
            "amount": random.randint(100000, 5000000),
            "approval_time": f"{random.randint(8, 17)}:00",
            "loan_date": f"2025-01-{random.randint(1, 28):02d}",
        })

    # Train the model
    detector = AutoencoderAnomalyDetector()

    print("Training autoencoder...")
    if detector.fit(sample_transactions):
        print("Training complete!")

        # Test with a normal transaction
        normal_tx = {
            "amount": 1000000,
            "approval_time": "10:30",
            "loan_date": "2025-01-15",
        }
        score, is_anomaly = detector.predict(normal_tx)
        print(f"Normal transaction: score={score:.3f}, anomaly={is_anomaly}")

        # Test with an anomalous transaction (large amount, late time)
        anomaly_tx = {
            "amount": 50000000,
            "approval_time": "23:45",
            "loan_date": "2025-01-15",
        }
        score, is_anomaly = detector.predict(anomaly_tx)
        print(f"Suspicious transaction: score={score:.3f}, anomaly={is_anomaly}")
    else:
        print("Training failed. Install tensorflow: pip install tensorflow")
