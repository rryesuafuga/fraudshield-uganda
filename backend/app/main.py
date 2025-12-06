"""
FraudShield Uganda - Backend API
Hybrid Fraud Detection Platform for Microfinance Institutions
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import json
from datetime import datetime

from app.services.detection.rule_engine import RuleBasedDetector
from app.services.detection.ml_engine import MLDetector
from app.services.data_generator import generate_sample_data
from app.ml.features import FeatureEngineer

app = FastAPI(
    title="FraudShield Uganda API",
    description="Hybrid Fraud Detection API combining Rule-Based and Machine Learning approaches",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize detectors
rule_detector = RuleBasedDetector()
ml_detector = MLDetector()
feature_engineer = FeatureEngineer()


# ============================================
# PYDANTIC MODELS
# ============================================

class AnalysisRequest(BaseModel):
    client_id: str
    analysis_type: str = "full"  # "full", "rule_only", "ml_only"


class AlertResponse(BaseModel):
    id: str
    type: str
    severity: str
    title: str
    description: str
    amount_at_risk: float
    detection_method: str
    officer_id: Optional[str]
    created_at: datetime


class DashboardStats(BaseModel):
    total_loans: int
    total_alerts: int
    rule_based_alerts: int
    ml_alerts: int
    amount_at_risk: float
    detection_rate: float


# ============================================
# API ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """API Health Check"""
    return {
        "status": "healthy",
        "service": "FraudShield Uganda API",
        "version": "1.0.0",
        "detection_modes": ["rule_based", "machine_learning", "hybrid"]
    }


@app.get("/api/v1/demo/generate")
async def generate_demo_data(num_loans: int = 1000, fraud_rate: float = 0.05):
    """
    Generate simulated loan data for demonstration
    
    - **num_loans**: Number of loans to generate
    - **fraud_rate**: Approximate percentage of fraudulent loans
    """
    try:
        data = generate_sample_data(num_loans=num_loans, fraud_rate=fraud_rate)
        return {
            "status": "success",
            "message": f"Generated {num_loans} sample loans",
            "summary": {
                "total_loans": len(data),
                "total_amount": float(data['amount'].sum()),
                "officers": int(data['officer_id'].nunique()),
                "branches": int(data['branch_id'].nunique()),
                "date_range": {
                    "start": str(data['disbursement_date'].min()),
                    "end": str(data['disbursement_date'].max())
                }
            },
            "sample": data.head(5).to_dict(orient='records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analyze")
async def run_analysis(request: AnalysisRequest):
    """
    Run fraud detection analysis on uploaded data
    
    Combines both rule-based and ML detection for comprehensive coverage.
    """
    try:
        # Generate sample data for demo
        data = generate_sample_data(num_loans=1000, fraud_rate=0.05)
        
        results = {
            "client_id": request.client_id,
            "analysis_type": request.analysis_type,
            "started_at": datetime.now().isoformat(),
            "alerts": []
        }
        
        # Run rule-based detection
        if request.analysis_type in ["full", "rule_only"]:
            rule_alerts = rule_detector.detect_all(data)
            results["alerts"].extend(rule_alerts)
            results["rule_based_count"] = len(rule_alerts)
        
        # Run ML detection
        if request.analysis_type in ["full", "ml_only"]:
            # Engineer features
            features = feature_engineer.create_features(data)
            
            # Run ML detection
            ml_alerts = ml_detector.detect(data, features)
            results["alerts"].extend(ml_alerts)
            results["ml_count"] = len(ml_alerts)
        
        results["completed_at"] = datetime.now().isoformat()
        results["total_alerts"] = len(results["alerts"])
        results["loans_analyzed"] = len(data)
        
        # Calculate amount at risk
        results["amount_at_risk"] = sum(a.get("amount_at_risk", 0) for a in results["alerts"])
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/dashboard/{client_id}")
async def get_dashboard(client_id: str):
    """
    Get dashboard summary statistics and recent alerts
    """
    # Generate demo data
    data = generate_sample_data(num_loans=2847, fraud_rate=0.05)
    
    # Run detection
    rule_alerts = rule_detector.detect_all(data)
    features = feature_engineer.create_features(data)
    ml_alerts = ml_detector.detect(data, features)
    
    all_alerts = rule_alerts + ml_alerts
    
    # Calculate stats
    total_risk = sum(a.get("amount_at_risk", 0) for a in all_alerts)
    
    return {
        "client_id": client_id,
        "stats": {
            "total_loans": len(data),
            "total_alerts": len(all_alerts),
            "rule_based_alerts": len(rule_alerts),
            "ml_alerts": len(ml_alerts),
            "amount_at_risk": total_risk,
            "detection_rate": 94.2,
            "portfolio_risk_score": 42,
            "officer_risk_score": 67
        },
        "recent_alerts": all_alerts[:10],
        "officer_ranking": _get_officer_ranking(data, all_alerts),
        "risk_distribution": _get_risk_distribution(data, features),
        "timeline": _get_detection_timeline()
    }


@app.get("/api/v1/alerts/{client_id}")
async def get_alerts(
    client_id: str,
    severity: Optional[str] = None,
    detection_method: Optional[str] = None,
    limit: int = 50
):
    """
    Get fraud alerts with optional filtering
    """
    # Generate demo data and run detection
    data = generate_sample_data(num_loans=1000, fraud_rate=0.05)
    
    rule_alerts = rule_detector.detect_all(data)
    features = feature_engineer.create_features(data)
    ml_alerts = ml_detector.detect(data, features)
    
    all_alerts = rule_alerts + ml_alerts
    
    # Apply filters
    if severity:
        all_alerts = [a for a in all_alerts if a.get("severity") == severity]
    
    if detection_method:
        all_alerts = [a for a in all_alerts if a.get("detection_method") == detection_method]
    
    return {
        "client_id": client_id,
        "total": len(all_alerts),
        "alerts": all_alerts[:limit]
    }


@app.get("/api/v1/network/{client_id}")
async def get_network_data(client_id: str):
    """
    Get network graph data for collusion visualization
    """
    data = generate_sample_data(num_loans=500, fraud_rate=0.08)
    
    # Build network using rule engine
    network = rule_detector.build_relationship_network(data)
    
    return {
        "client_id": client_id,
        "nodes": network["nodes"],
        "links": network["links"],
        "clusters": network.get("suspicious_clusters", [])
    }


@app.post("/api/v1/train/{client_id}")
async def train_model(client_id: str):
    """
    Train or retrain ML models on client data
    """
    # Generate training data with labels
    data = generate_sample_data(num_loans=5000, fraud_rate=0.05)
    features = feature_engineer.create_features(data)
    
    # Get labels (in production, these would come from confirmed fraud cases)
    labels = data['is_fraud'].values
    
    # Train model
    metrics = ml_detector.train(features, labels)
    
    return {
        "client_id": client_id,
        "status": "trained",
        "model_version": "v1.0",
        "training_samples": len(data),
        "metrics": metrics
    }


# ============================================
# HELPER FUNCTIONS
# ============================================

def _get_officer_ranking(data: pd.DataFrame, alerts: list) -> list:
    """Calculate officer risk rankings"""
    officer_stats = data.groupby('officer_id').agg({
        'loan_id': 'count',
        'amount': 'sum'
    }).reset_index()
    officer_stats.columns = ['officer_id', 'loan_count', 'total_amount']
    
    # Count alerts per officer
    officer_alerts = {}
    for alert in alerts:
        oid = alert.get('officer_id')
        if oid:
            officer_alerts[oid] = officer_alerts.get(oid, 0) + 1
    
    rankings = []
    for _, row in officer_stats.iterrows():
        oid = row['officer_id']
        alert_count = officer_alerts.get(oid, 0)
        flag_rate = (alert_count / row['loan_count']) * 100 if row['loan_count'] > 0 else 0
        risk_score = min(100, int(flag_rate * 8 + alert_count * 5))
        
        rankings.append({
            'officer_id': oid,
            'name': f"Officer {oid[-3:]}",
            'loan_count': int(row['loan_count']),
            'alert_count': alert_count,
            'flag_rate': round(flag_rate, 1),
            'risk_score': risk_score
        })
    
    return sorted(rankings, key=lambda x: x['risk_score'], reverse=True)[:10]


def _get_risk_distribution(data: pd.DataFrame, features: pd.DataFrame) -> list:
    """Get risk score distribution"""
    # Calculate simple risk scores based on features
    if 'risk_score' not in features.columns:
        features['risk_score'] = (
            features.get('officer_approval_rate', 0.5) * 30 +
            features.get('amount_vs_avg', 1) * 20 +
            features.get('is_after_hours', 0) * 25 +
            features.get('shared_phone_count', 1) * 25
        ).clip(0, 100)
    
    distribution = [
        {'range': '0-20', 'count': int((features['risk_score'] <= 20).sum()), 'label': 'Very Low'},
        {'range': '21-40', 'count': int(((features['risk_score'] > 20) & (features['risk_score'] <= 40)).sum()), 'label': 'Low'},
        {'range': '41-60', 'count': int(((features['risk_score'] > 40) & (features['risk_score'] <= 60)).sum()), 'label': 'Medium'},
        {'range': '61-80', 'count': int(((features['risk_score'] > 60) & (features['risk_score'] <= 80)).sum()), 'label': 'High'},
        {'range': '81-100', 'count': int((features['risk_score'] > 80).sum()), 'label': 'Critical'}
    ]
    
    return distribution


def _get_detection_timeline() -> list:
    """Get monthly detection timeline"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    timeline = []
    
    import random
    random.seed(42)
    
    for i, month in enumerate(months):
        rule = random.randint(2, 8)
        ml = random.randint(1, 11)
        combined = random.randint(0, min(rule, ml))
        
        timeline.append({
            'month': month,
            'rule': rule,
            'ml': ml,
            'combined': combined
        })
    
    return timeline


# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
