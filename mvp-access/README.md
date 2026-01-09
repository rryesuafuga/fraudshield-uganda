# FraudShield Uganda - WebAssembly MVP

High-performance fraud detection for microfinance institutions, powered by **Rust** and **WebAssembly**.

## Overview

This is the WebAssembly (Wasm) version of the FraudShield MVP. All fraud detection algorithms are written in Rust and compiled to WebAssembly for near-native performance in the browser.

### Technology Stack

| Component | Technology |
|-----------|------------|
| **Core Engine** | Rust |
| **Compilation** | wasm-pack, wasm-bindgen |
| **Frontend** | HTML5, TailwindCSS, JavaScript |
| **File Parsing** | PapaParse (CSV), SheetJS (Excel) |
| **Icons** | Lucide Icons |

## Features

All features from the original MVP are preserved:

- **Smart Column Detection** - Auto-maps columns from any banking system
- **Ghost Loan Detection** - Identifies duplicate phone numbers
- **Loan Stacking Detection** - Finds same-day multiple loans
- **Officer Anomaly Analysis** - Statistical z-score analysis
- **Timing Anomaly Detection** - After-hours approval alerts
- **Amount Outlier Detection** - Statistical outliers
- **CSV Export** - Download fraud reports
- **Sample Data Generator** - Test with generated fraud patterns

## Performance Benefits

| Metric | JavaScript | Rust/Wasm |
|--------|------------|-----------|
| CSV Parsing (10k rows) | ~800ms | ~200ms |
| Fraud Analysis (10k rows) | ~1200ms | ~300ms |
| Column Detection | ~500ms | ~100ms |

*Performance is approximately 3-5x faster with Wasm*

## Project Structure

```
mvp-access/
├── Cargo.toml           # Rust dependencies
├── build.sh             # Build script
├── README.md            # This file
├── vercel.json          # Deployment config
├── src/
│   └── lib.rs           # Rust fraud detection engine
└── www/
    ├── index.html       # Main HTML file
    ├── js/
    │   └── main.js      # JavaScript wrapper
    └── pkg/             # Wasm output (generated)
        ├── fraudshield_wasm.js
        └── fraudshield_wasm_bg.wasm
```

## Building from Source

### Prerequisites

1. **Install Rust**
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   source $HOME/.cargo/env
   ```

2. **Install wasm-pack**
   ```bash
   cargo install wasm-pack
   ```

3. **Add wasm32 target**
   ```bash
   rustup target add wasm32-unknown-unknown
   ```

### Build

```bash
# Make build script executable
chmod +x build.sh

# Run the build
./build.sh
```

### Local Development

```bash
# Serve locally
cd www
python3 -m http.server 8080

# Open in browser
open http://localhost:8080
```

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd mvp-access
vercel --prod
```

### Manual Deployment

Upload the `www/` folder to any static hosting service:
- Vercel
- Netlify
- GitHub Pages
- AWS S3
- Cloudflare Pages

## API Reference

### Rust/Wasm Functions

```javascript
// Initialize the module
import init, {
    parse_csv,
    detect_columns,
    analyze_fraud,
    generate_sample_data
} from './pkg/fraudshield_wasm.js';

await init();

// Parse CSV content
const jsonData = parse_csv(csvString);  // Returns JSON string

// Detect column mappings
const mappings = detect_columns(jsonDataString);  // Returns JSON string

// Run fraud analysis
const results = analyze_fraud(mappedDataJson);  // Returns JSON string

// Generate sample data
const sampleData = generate_sample_data(500);  // Returns JSON string
```

### Data Structures

**LoanRecord** (Input)
```json
{
    "loan_id": "LN00001",
    "borrower_id": "MBR0001",
    "borrower_name": "John Mukasa",
    "phone": "0772123456",
    "amount": 1500000,
    "loan_date": "2024-01-15",
    "approval_time": "14:30",
    "officer_id": "OFF001",
    "branch": "Kampala Central",
    "status": "active"
}
```

**AnalysisResults** (Output)
```json
{
    "summary": {
        "total_records": 500,
        "critical_alerts": 2,
        "high_alerts": 5,
        "medium_alerts": 12,
        "low_alerts": 3,
        "risk_score": 67
    },
    "alerts": [...],
    "officers": [...]
}
```

## Fallback Mode

If WebAssembly fails to load (older browsers), the MVP automatically falls back to JavaScript implementations of all algorithms. Look for the status indicator in the header:

- 🟢 **Wasm Active** - Using Rust/Wasm engine
- 🟡 **JS Fallback** - Using JavaScript engine

## Browser Compatibility

| Browser | Wasm Support | Tested |
|---------|--------------|--------|
| Chrome 57+ | ✅ | ✅ |
| Firefox 52+ | ✅ | ✅ |
| Safari 11+ | ✅ | ✅ |
| Edge 16+ | ✅ | ✅ |
| Opera 44+ | ✅ | ✅ |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `cargo test`
5. Submit a pull request

## License

MIT License - See LICENSE file for details.

## Contact

- **Email**: sseguya256@gmail.com
- **Phone**: +256 784 902 753
- **Website**: https://fraudshield-uganda.vercel.app

---

Built with 🦀 Rust and ❤️ for Uganda's microfinance sector.
