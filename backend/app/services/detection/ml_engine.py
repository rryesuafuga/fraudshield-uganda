"""
Machine Learning Detection Engine
Adaptive fraud detection that learns from client data patterns
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import pickle
import os


class MLDetector:
    """
    Machine Learning based fraud detection that learns institution-specific patterns.
    Uses both unsupervised (Isolation Forest) and supervised (Gradient Boosting) methods.
    """
    
    def __init__(self, model_dir: str = "./models"):
        self.model_dir = model_dir
        self.scaler = StandardScaler()
        
        # Unsupervised model (works without labels)
        self.isolation_forest = IsolationForest(
            contamination=0.05,  # Expected fraud rate
            random_state=42,
            n_estimators=100,
            max_samples='auto'
        )
        
        # Supervised model (requires labeled data)
        self.supervised_model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        
        self.is_fitted = False
        self.supervised_fitted = False
        
        # Feature columns used for training
        self.feature_columns = None
        
        # Model metadata
        self.metadata = {
            'version': '1.0',
            'created_at': None,
            'training_samples': 0,
            'feature_count': 0,
            'metrics': {}
        }
    
    def detect(self, data: pd.DataFrame, features: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Run ML-based fraud detection
        
        Parameters:
        -----------
        data : pd.DataFrame
            Original loan data with metadata
        features : pd.DataFrame
            Engineered features for ML
            
        Returns:
        --------
        List[Dict]
            List of fraud alerts
        """
        alerts = []
        
        # Ensure features are numeric
        numeric_features = features.select_dtypes(include=[np.number])
        
        if len(numeric_features.columns) == 0:
            return alerts
        
        # Handle missing values
        numeric_features = numeric_features.fillna(0)
        
        # Scale features
        try:
            if not self.is_fitted:
                # First time - fit and transform
                X_scaled = self.scaler.fit_transform(numeric_features)
                self.isolation_forest.fit(X_scaled)
                self.is_fitted = True
            else:
                X_scaled = self.scaler.transform(numeric_features)
        except Exception as e:
            print(f"Scaling error: {e}")
            return alerts
        
        # Get anomaly scores from Isolation Forest
        anomaly_scores = self.isolation_forest.decision_function(X_scaled)
        predictions = self.isolation_forest.predict(X_scaled)
        
        # Normalize scores to 0-100 risk score
        min_score = anomaly_scores.min()
        max_score = anomaly_scores.max()
        if max_score - min_score > 0:
            risk_scores = 100 * (1 - (anomaly_scores - min_score) / (max_score - min_score))
        else:
            risk_scores = np.zeros(len(anomaly_scores))
        
        # Add supervised predictions if model is fitted
        if self.supervised_fitted:
            try:
                supervised_proba = self.supervised_model.predict_proba(X_scaled)[:, 1]
                # Combine scores (60% supervised, 40% unsupervised)
                combined_scores = 0.6 * (supervised_proba * 100) + 0.4 * risk_scores
            except:
                combined_scores = risk_scores
        else:
            combined_scores = risk_scores
        
        # Generate alerts for high-risk predictions
        high_risk_mask = (predictions == -1) | (combined_scores > 70)
        high_risk_indices = np.where(high_risk_mask)[0]
        
        for idx in high_risk_indices:
            if idx >= len(data):
                continue
                
            row = data.iloc[idx]
            score = combined_scores[idx]
            
            # Determine severity
            if score > 85:
                severity = 'high'
            elif score > 70:
                severity = 'medium'
            else:
                severity = 'low'
            
            # Identify primary risk factors
            risk_factors = self._identify_risk_factors(features.iloc[idx], numeric_features.columns)
            
            # Determine alert type based on risk factors
            alert_type = self._determine_alert_type(risk_factors)
            
            alerts.append({
                'id': str(uuid.uuid4()),
                'type': alert_type,
                'severity': severity,
                'title': f'ML-Detected Anomaly: {alert_type.replace("_", " ").title()}',
                'description': f"Machine learning model flagged this loan with {score:.0f}% risk score. " +
                              f"Key factors: {', '.join(risk_factors[:3])}",
                'amount_at_risk': float(row.get('amount', 0)),
                'detection_method': 'ml',
                'officer_id': row.get('officer_id'),
                'affected_loans': [row.get('loan_id', str(idx))],
                'evidence': {
                    'risk_score': float(score),
                    'anomaly_score': float(anomaly_scores[idx]),
                    'risk_factors': risk_factors,
                    'feature_values': {
                        k: float(v) if isinstance(v, (int, float, np.number)) else str(v)
                        for k, v in features.iloc[idx].items()
                        if k in risk_factors
                    }
                },
                'created_at': datetime.now().isoformat()
            })
        
        # Limit alerts and sort by risk score
        alerts = sorted(alerts, key=lambda x: x['evidence']['risk_score'], reverse=True)
        
        return alerts[:50]  # Return top 50 alerts
    
    def train(self, features: pd.DataFrame, labels: np.ndarray) -> Dict[str, Any]:
        """
        Train supervised model on labeled data
        
        Parameters:
        -----------
        features : pd.DataFrame
            Feature matrix
        labels : np.ndarray
            Binary labels (1 = fraud, 0 = normal)
            
        Returns:
        --------
        Dict
            Training metrics
        """
        # Select numeric features
        numeric_features = features.select_dtypes(include=[np.number]).fillna(0)
        self.feature_columns = numeric_features.columns.tolist()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(numeric_features)
        
        # Fit unsupervised model
        self.isolation_forest.fit(X_scaled)
        self.is_fitted = True
        
        # Split for supervised training
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Train supervised model
        self.supervised_model.fit(X_train, y_train)
        self.supervised_fitted = True
        
        # Evaluate
        y_pred = self.supervised_model.predict(X_test)
        y_proba = self.supervised_model.predict_proba(X_test)[:, 1]
        
        metrics = {
            'precision': float(precision_score(y_test, y_pred, zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred, zero_division=0)),
            'roc_auc': float(roc_auc_score(y_test, y_proba)) if len(np.unique(y_test)) > 1 else 0.0,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'fraud_rate_train': float(y_train.mean()),
            'fraud_rate_test': float(y_test.mean())
        }
        
        # Cross-validation score
        cv_scores = cross_val_score(self.supervised_model, X_scaled, labels, cv=5, scoring='f1')
        metrics['cv_f1_mean'] = float(cv_scores.mean())
        metrics['cv_f1_std'] = float(cv_scores.std())
        
        # Feature importance
        importance = self.supervised_model.feature_importances_
        feature_importance = sorted(
            zip(self.feature_columns, importance),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        metrics['top_features'] = [
            {'feature': f, 'importance': float(i)} 
            for f, i in feature_importance
        ]
        
        # Update metadata
        self.metadata['created_at'] = datetime.now().isoformat()
        self.metadata['training_samples'] = len(X_scaled)
        self.metadata['feature_count'] = len(self.feature_columns)
        self.metadata['metrics'] = metrics
        
        return metrics
    
    def predict_risk_scores(self, features: pd.DataFrame) -> np.ndarray:
        """
        Generate risk scores for all loans
        
        Returns:
        --------
        np.ndarray
            Array of risk scores (0-100)
        """
        numeric_features = features.select_dtypes(include=[np.number]).fillna(0)
        
        if not self.is_fitted:
            X_scaled = self.scaler.fit_transform(numeric_features)
            self.isolation_forest.fit(X_scaled)
            self.is_fitted = True
        else:
            X_scaled = self.scaler.transform(numeric_features)
        
        # Isolation Forest scores
        iso_scores = self.isolation_forest.decision_function(X_scaled)
        iso_normalized = 100 * (1 - (iso_scores - iso_scores.min()) / 
                                (iso_scores.max() - iso_scores.min() + 1e-10))
        
        if self.supervised_fitted:
            supervised_proba = self.supervised_model.predict_proba(X_scaled)[:, 1] * 100
            return 0.6 * supervised_proba + 0.4 * iso_normalized
        
        return iso_normalized
    
    def _identify_risk_factors(self, row: pd.Series, columns: list) -> List[str]:
        """Identify which features contributed most to high risk score"""
        risk_factors = []
        
        # Check specific conditions
        if 'officer_volume_z' in row.index and abs(row.get('officer_volume_z', 0)) > 2:
            risk_factors.append('unusual_officer_volume')
        
        if 'amount_vs_avg' in row.index and row.get('amount_vs_avg', 1) > 2:
            risk_factors.append('high_loan_amount')
        
        if 'is_after_hours' in row.index and row.get('is_after_hours', 0) > 0:
            risk_factors.append('after_hours_transaction')
        
        if 'shared_phone_count' in row.index and row.get('shared_phone_count', 1) > 1:
            risk_factors.append('shared_phone_number')
        
        if 'shared_guarantor_count' in row.index and row.get('shared_guarantor_count', 1) > 2:
            risk_factors.append('shared_guarantor')
        
        if 'officer_approval_rate' in row.index and row.get('officer_approval_rate', 0.7) > 0.9:
            risk_factors.append('high_officer_approval_rate')
        
        if 'loan_count' in row.index and row.get('loan_count', 1) > 3:
            risk_factors.append('multiple_loans')
        
        if 'geographic_density' in row.index and row.get('geographic_density', 0) > 5:
            risk_factors.append('geographic_clustering')
        
        # If no specific factors found, use generic
        if not risk_factors:
            risk_factors.append('statistical_anomaly')
        
        return risk_factors
    
    def _determine_alert_type(self, risk_factors: List[str]) -> str:
        """Determine alert type based on risk factors"""
        if 'shared_phone_number' in risk_factors:
            return 'ghost_loan'
        elif 'geographic_clustering' in risk_factors or 'shared_guarantor' in risk_factors:
            return 'collusion_pattern'
        elif 'unusual_officer_volume' in risk_factors or 'high_officer_approval_rate' in risk_factors:
            return 'officer_anomaly'
        elif 'after_hours_transaction' in risk_factors:
            return 'timing_anomaly'
        elif 'multiple_loans' in risk_factors:
            return 'loan_stacking'
        elif 'high_loan_amount' in risk_factors:
            return 'amount_anomaly'
        else:
            return 'ml_anomaly'
    
    def save_model(self, path: str = None):
        """Save trained model to disk"""
        if path is None:
            path = os.path.join(self.model_dir, 'fraud_detector.pkl')
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        model_data = {
            'scaler': self.scaler,
            'isolation_forest': self.isolation_forest,
            'supervised_model': self.supervised_model if self.supervised_fitted else None,
            'feature_columns': self.feature_columns,
            'is_fitted': self.is_fitted,
            'supervised_fitted': self.supervised_fitted,
            'metadata': self.metadata
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        return path
    
    def load_model(self, path: str = None):
        """Load trained model from disk"""
        if path is None:
            path = os.path.join(self.model_dir, 'fraud_detector.pkl')
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model not found at {path}")
        
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.scaler = model_data['scaler']
        self.isolation_forest = model_data['isolation_forest']
        self.feature_columns = model_data['feature_columns']
        self.is_fitted = model_data['is_fitted']
        self.supervised_fitted = model_data['supervised_fitted']
        self.metadata = model_data['metadata']
        
        if model_data['supervised_model'] is not None:
            self.supervised_model = model_data['supervised_model']
    
    def get_feature_importance(self) -> List[Dict[str, Any]]:
        """Get feature importance from supervised model"""
        if not self.supervised_fitted:
            return []
        
        importance = self.supervised_model.feature_importances_
        result = []
        
        for feature, imp in zip(self.feature_columns, importance):
            result.append({
                'feature': feature,
                'importance': float(imp)
            })
        
        return sorted(result, key=lambda x: x['importance'], reverse=True)


if __name__ == "__main__":
    # Test ML detector
    from app.services.data_generator import generate_sample_data
    from app.ml.features import FeatureEngineer
    
    # Generate data
    data = generate_sample_data(1000, 0.05)
    print(f"Generated {len(data)} loans")
    
    # Engineer features
    fe = FeatureEngineer()
    features = fe.create_features(data)
    print(f"Created {len(features.columns)} features")
    
    # Initialize detector
    detector = MLDetector()
    
    # Run detection (unsupervised)
    alerts = detector.detect(data, features)
    print(f"\nUnsupervised Detection: {len(alerts)} alerts")
    
    # Train with labels
    labels = data['is_fraud'].astype(int).values
    metrics = detector.train(features, labels)
    print(f"\nTraining Metrics:")
    for k, v in metrics.items():
        if k != 'top_features':
            print(f"  {k}: {v}")
    
    # Run detection again (now with supervised)
    alerts = detector.detect(data, features)
    print(f"\nSupervised Detection: {len(alerts)} alerts")
    
    if alerts:
        print(f"\nSample alert:")
        import json
        print(json.dumps(alerts[0], indent=2, default=str))
