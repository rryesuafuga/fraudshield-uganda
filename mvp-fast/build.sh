#!/bin/bash
# FraudShield Uganda - Fast Edition Build Script
# Compiles Rust to WebAssembly

set -e

echo "Building FraudShield Fast Edition..."

# Check for wasm-pack
if ! command -v wasm-pack &> /dev/null; then
    echo "Installing wasm-pack..."
    curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh
fi

# Build the Wasm module
echo "Compiling Rust to WebAssembly..."
wasm-pack build --target web --out-dir www/pkg

echo "Build complete!"
echo "To run locally: cd www && python3 -m http.server 8080"
echo "Then open http://localhost:8080"
