"""
FraudShield Uganda - ML Model Integrations

This package provides integration examples for various fraud detection models.
"""

from .huggingface_integration import HuggingFacePredictor
from .autoencoder_integration import AutoencoderAnomalyDetector
from .ensemble_integration import FraudEnsemble, ModelType

__all__ = [
    "HuggingFacePredictor",
    "AutoencoderAnomalyDetector",
    "FraudEnsemble",
    "ModelType",
]
