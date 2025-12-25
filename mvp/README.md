# FraudShield Uganda MVP

AI-Powered Fraud Detection Platform for Microfinance Institutions and SACCOs in Uganda.

## Features

### Smart Column Mapping
Our AI automatically detects and maps columns from your CSV/Excel files, regardless of naming conventions:
- **Pattern Detection**: Recognizes phone numbers, dates, amounts, IDs
- **Fuzzy Matching**: Matches similar column names (e.g., "mobile_number" → "phone")
- **Statistical Analysis**: Infers column types from data characteristics

### Fraud Detection Rules
1. **Ghost Loans**: Detects duplicate phone numbers across different borrowers
2. **Loan Stacking**: Identifies borrowers with multiple loans on the same day
3. **Officer Anomalies**: Flags officers with unusually high loan volumes
4. **Timing Anomalies**: Detects after-hours loan approvals
5. **Amount Outliers**: Identifies loans significantly above average

### MVP Capabilities
- Upload CSV or Excel files
- Automatic column type detection
- Real-time fraud analysis
- Interactive results dashboard
- Downloadable reports

## How to Use

1. **Open the MVP**: Open `index.html` in a web browser or deploy to Netlify/Vercel
2. **Upload Data**: Upload your loan data (CSV/Excel) or use sample data
3. **Review Mappings**: Verify the auto-detected column mappings
4. **Analyze**: Run fraud detection analysis
5. **Review Results**: Examine alerts, officer rankings, and risk scores

## Expected CSV Format

While the system accepts any column names, here are the recommended fields:

```csv
loan_id,borrower_id,borrower_name,phone,amount,loan_date,approval_time,officer_id,branch,status
```

Supported column name variations:
| Standard Field | Accepted Variations |
|---------------|---------------------|
| loan_id | loan_no, ref_no, reference, contract_id |
| borrower_id | member_id, client_id, customer_id |
| borrower_name | name, full_name, member_name |
| phone | mobile, telephone, contact, phone_number |
| amount | loan_amount, principal, disbursed_amount |
| officer_id | staff_id, approved_by, agent_id |
| branch | branch_name, office, location |

## Deployment

### Netlify (Recommended)
1. Drag & drop the `mvp` folder to [netlify.com/drop](https://netlify.com/drop)
2. Or connect GitHub and set publish directory to `mvp`
3. Configuration is in `netlify.toml`

### Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Navigate to mvp folder: `cd mvp`
3. Deploy: `vercel`
4. Or connect GitHub repository at [vercel.com](https://vercel.com)
5. Set root directory to `mvp`
6. Configuration is in `vercel.json`

**Vercel Features:**
- Free tier: Unlimited personal projects
- Automatic HTTPS & global CDN
- Preview deployments for PRs

### GitHub Pages
1. Go to repository Settings → Pages
2. Set source to main branch, folder `/mvp`
3. Save and wait for deployment

### Full Stack (with Backend)
1. Deploy backend to Railway, Render, or AWS
2. Update frontend API endpoint
3. Deploy frontend to Netlify/Vercel

## Tech Stack

### Frontend
- HTML5, Tailwind CSS
- Vanilla JavaScript
- PapaParse (CSV parsing)
- SheetJS (Excel parsing)
- Lucide Icons

### Backend
- Python 3.9+
- FastAPI
- pandas, scikit-learn
- Isolation Forest, Gradient Boosting

## Contact

- **Email**: sseguya256@gmail.com
- **Phone**: +256 784 902 753
- **Website**: fraudshield-uganda.netlify.app

---

© 2025 FraudShield Uganda | MVP Version
