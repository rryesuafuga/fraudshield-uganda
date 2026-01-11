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

### Automatic Deployment (GitHub Actions)

This project includes GitHub Actions CI/CD that automatically:
1. Builds the Rust code to WebAssembly
2. Deploys to Vercel and/or GitHub Pages

The workflow triggers on:
- Push to `main` or `master` branch (when `mvp-fast/` files change)
- Pull requests to `main` or `master`
- Manual trigger via `workflow_dispatch`

#### Setting up Vercel Deployment

To enable automatic Vercel deployment, add these secrets to your GitHub repository:

1. Go to **Settings → Secrets and variables → Actions**
2. Add these secrets:
   - `VERCEL_TOKEN` - Get from [Vercel Account Settings](https://vercel.com/account/tokens)
   - `VERCEL_ORG_ID` - Found in `.vercel/project.json` after running `vercel link`
   - `VERCEL_PROJECT_ID` - Found in `.vercel/project.json` after running `vercel link`

#### GitHub Pages Deployment

GitHub Pages deployment is enabled by default. The workflow will automatically:
1. Build the Wasm module
2. Upload to GitHub Pages
3. Deploy at `https://<username>.github.io/<repo>/`

To enable GitHub Pages:
1. Go to **Settings → Pages**
2. Set **Source** to "GitHub Actions"

### Manual Vercel Deployment

The `vercel.json` is pre-configured. Just connect the repository to Vercel and set:
- **Root Directory**: `mvp-fast`
- **Build Command**: `./build.sh` (or leave empty if pre-built via CI)
- **Output Directory**: `www`

### Manual Deployment

Upload the contents of the `www` folder (including `pkg/` after build) to any static hosting service.

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

