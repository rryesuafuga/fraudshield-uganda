# FraudShield Uganda - Backend API

Hybrid Fraud Detection Platform for Microfinance Institutions

## Overview

This is the backend API for FraudShield Uganda, featuring a hybrid fraud detection approach:

1. **Rule-Based Detection** - Statistical pattern recognition that works immediately without training
2. **Machine Learning Detection** - Adaptive models that learn institution-specific patterns over time

## Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
# Development mode
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
fraudshield-backend/
├── app/
│   ├── main.py                      # FastAPI application entry point
│   ├── api/                         # API routes
│   ├── services/
│   │   ├── data_generator.py        # Sample data generation
│   │   └── detection/
│   │       ├── rule_engine.py       # Rule-based detection
│   │       └── ml_engine.py         # Machine learning detection
│   └── ml/
│       └── features.py              # Feature engineering
├── data/                            # Data storage
├── tests/                           # Test files
└── requirements.txt
```

## API Endpoints

### Health Check
```
GET /
```

### Generate Demo Data
```
GET /api/v1/demo/generate?num_loans=1000&fraud_rate=0.05
```

### Run Analysis
```
POST /api/v1/analyze
{
    "client_id": "client_123",
    "analysis_type": "full"  // "full", "rule_only", "ml_only"
}
```

### Get Dashboard Data
```
GET /api/v1/dashboard/{client_id}
```

### Get Alerts
```
GET /api/v1/alerts/{client_id}?severity=high&detection_method=ml&limit=50
```

### Get Network Graph
```
GET /api/v1/network/{client_id}
```

### Train ML Model
```
POST /api/v1/train/{client_id}
```

## Detection Methods

### Rule-Based Detection

Works immediately without training data:

- **Ghost Loan Detection** - Identifies shared phone numbers across borrowers
- **Officer Anomaly Detection** - Z-score analysis of officer activity
- **Geographic Clustering** - Finds suspicious loan clusters
- **Timing Anomalies** - After-hours transactions
- **Shared Guarantor Networks** - Network analysis of guarantor relationships
- **Loan Stacking** - Multiple active loans per borrower

### Machine Learning Detection

Learns from data over time:

- **Isolation Forest** - Unsupervised anomaly detection (works without labels)
- **Gradient Boosting** - Supervised classification (requires labeled fraud cases)
- **Risk Scoring** - 0-100 risk score for every loan
- **Feature Importance** - Identifies key fraud indicators

## Feature Engineering

The ML engine uses 30+ engineered features:

- **Amount Features**: Loan amount relative to averages, percentiles
- **Officer Features**: Activity volume, approval rates, Z-scores
- **Temporal Features**: Hour, day, weekend, month-end indicators
- **Network Features**: Shared phones, guarantors, addresses
- **Geographic Features**: Density clustering, officer concentration
- **Borrower Features**: Multiple loans, multi-branch activity

## Security Considerations

For production deployment:

1. Enable HTTPS (TLS)
2. Implement proper authentication (JWT)
3. Add rate limiting
4. Encrypt sensitive data at rest
5. Enable audit logging
6. Set up monitoring and alerts

## Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/fraudshield
REDIS_URL=redis://localhost:6379/0
DEBUG=true
```

## License

Proprietary - FraudShield Uganda

## Author

Raymond R. Wayesu
Data Analytics Lead, UVRI
sseguya256@gmail.com
