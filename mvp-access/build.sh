#!/bin/bash

# FraudShield Uganda - Wasm MVP Build Script
# This script builds the Rust code to WebAssembly

set -e

echo "🦀 FraudShield Uganda - Wasm MVP Build"
echo "======================================="

# Check for required tools
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        echo "   Install with: $2"
        exit 1
    fi
}

check_tool rustc "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
check_tool wasm-pack "cargo install wasm-pack"

echo "✅ All required tools are installed"
echo ""

# Add wasm32 target if not present
echo "📦 Adding wasm32 target..."
rustup target add wasm32-unknown-unknown 2>/dev/null || true

# Build the Wasm package
echo "🔨 Building Wasm package..."
wasm-pack build --target web --out-dir www/pkg --release

# Clean up unnecessary files
echo "🧹 Cleaning up..."
rm -f www/pkg/.gitignore
rm -f www/pkg/package.json

echo ""
echo "✅ Build complete!"
echo ""
echo "📁 Output files in: www/pkg/"
echo "   - fraudshield_wasm.js"
echo "   - fraudshield_wasm_bg.wasm"
echo ""
echo "🚀 To serve locally:"
echo "   cd www && python3 -m http.server 8080"
echo "   Then open http://localhost:8080"
echo ""
echo "🌐 To deploy to Vercel:"
echo "   vercel --prod"
