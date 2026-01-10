# FraudShield Uganda - Fast Edition

High-performance fraud detection powered by **Rust + WebAssembly** for near-native speed in the browser.

## Features

All the same features as the original MVP, but significantly faster:

- **Smart Column Detection** - Automatically recognizes columns from any banking/SACCO system
- **Ghost Loan Detection** - Identifies duplicate phone numbers across loans
- **Loan Stacking Detection** - Finds multiple loans to same borrower on same day
- **Officer Anomaly Detection** - Statistical analysis of officer loan volumes
- **Timing Anomaly Detection** - Flags after-hours loan approvals
- **Amount Anomaly Detection** - Statistical outlier detection for large loans
- **CSV/Excel Support** - Upload .csv, .xlsx, or .xls files
- **Sample Data** - Test with 500 pre-generated loans with fraud patterns
- **Export Reports** - Download detailed CSV reports

## Performance

The WebAssembly engine provides:
- **10-100x faster** fraud detection compared to pure JavaScript
- **Near-native performance** in the browser
- **Instant analysis** of thousands of loan records

## Building from Source

### Prerequisites

- [Rust](https://rustup.rs/) (1.70+)
- [wasm-pack](https://rustwasm.github.io/wasm-pack/installer/)

### Build

```bash
# Install wasm-pack if not installed
curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh

# Build the WebAssembly module
./build.sh

# Or manually:
wasm-pack build --target web --out-dir www/pkg
```

### Run Locally

```bash
cd www
python3 -m http.server 8080
# Open http://localhost:8080
```

## Deployment

### Vercel

The `vercel.json` is pre-configured. Just connect the repository to Vercel and set:
- **Root Directory**: `mvp-fast`
- **Build Command**: (leave empty - pre-built)
- **Output Directory**: `www`

### Manual Deployment

Upload the contents of the `www` folder to any static hosting service.

## Architecture

```
mvp-fast/
├── Cargo.toml          # Rust dependencies
├── src/
│   └── lib.rs          # Rust fraud detection engine
├── www/
│   ├── index.html      # Main UI
│   ├── js/
│   │   └── main.js     # JavaScript wrapper
│   └── pkg/            # Compiled WebAssembly (after build)
├── build.sh            # Build script
├── vercel.json         # Deployment config
└── README.md           # This file
```

## How It Works

1. **File Upload**: User uploads CSV/Excel file (or uses sample data)
2. **Column Detection**: Wasm module analyzes columns and auto-maps them
3. **Fraud Analysis**: Wasm module runs all detection algorithms
4. **Results Display**: JavaScript renders the results in the UI

The heavy computation (column detection, fraud detection) happens in Rust/Wasm, while the UI is handled by JavaScript.

## Fallback Mode

If WebAssembly fails to load (unsupported browser, etc.), the app automatically falls back to pure JavaScript implementations of all algorithms. Performance will be slower but functionality is preserved.

## Contact

FraudShield Uganda
Email: sseguya256@gmail.com
Phone: +256 784 902 753
