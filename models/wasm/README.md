# WebAssembly & WebGPU Fraud Detection

Browser-based ML inference for FraudShield Uganda - no server required.

## Quick Start

### Using ONNX Runtime Web (Recommended)

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/onnxruntime-web/dist/ort.min.js"></script>
</head>
<body>
  <script>
    async function detectFraud(transaction) {
      // Load model (cached after first load)
      const session = await ort.InferenceSession.create('fraud_model.onnx', {
        executionProviders: ['wasm']
      });

      // Prepare features
      const features = extractFeatures(transaction);
      const input = new ort.Tensor('float32', features, [1, 15]);

      // Run inference
      const results = await session.run({ input: input });
      const fraudScore = results.output.data[0];

      return {
        score: fraudScore,
        isFraud: fraudScore > 0.5,
        risk: fraudScore > 0.7 ? 'HIGH' : fraudScore > 0.4 ? 'MEDIUM' : 'LOW'
      };
    }
  </script>
</body>
</html>
```

## Available Models

| Model | Source | Size | Latency | Best For |
|-------|--------|------|---------|----------|
| Hazelcast LightGBM | [GitHub](https://github.com/hazelcast/fraud-detection-onnx) | ~5MB | <0.1ms | Real-time scoring |
| IBM LSTM | [GitHub](https://github.com/IBM/ai-on-z-fraud-detection) | ~50MB | ~10ms | Transaction sequences |
| Extended Isolation Forest | Rust crate | ~2MB | ~1ms | Anomaly detection |

## Installation Options

### Option 1: CDN (Quickest)
```html
<script src="https://cdn.jsdelivr.net/npm/onnxruntime-web/dist/ort.min.js"></script>
```

### Option 2: NPM
```bash
npm install onnxruntime-web
```

### Option 3: Rust/WASM (tract)
```bash
cargo install tract
tract model.onnx run --target wasm32-wasi
```

## Feature Extraction

The models expect 15 standardized features:

```javascript
function extractFeatures(transaction) {
  return new Float32Array([
    transaction.amount,                    // 0: Transaction amount
    transaction.amount / avgAmount,        // 1: Amount ratio to average
    hourOfDay(transaction.time),           // 2: Hour (0-23)
    dayOfWeek(transaction.date),           // 3: Day (0-6)
    transaction.isWeekend ? 1 : 0,         // 4: Weekend flag
    transaction.isAfterHours ? 1 : 0,      // 5: After business hours
    transaction.customerAge,               // 6: Customer age in days
    transaction.transactionCount30d,       // 7: Transactions last 30 days
    transaction.avgAmount30d,              // 8: Average amount 30 days
    transaction.merchantCategory,          // 9: Merchant category code
    transaction.sameDevicePrev ? 1 : 0,    // 10: Same device as previous
    transaction.distanceFromPrev,          // 11: Distance from last transaction
    transaction.timeSincePrev,             // 12: Minutes since last transaction
    transaction.failedAttempts24h,         // 13: Failed attempts last 24h
    transaction.uniqueMerchants7d,         // 14: Unique merchants last 7 days
  ]);
}
```

## WebGPU Acceleration

For GPU-accelerated inference (2-10x faster):

```javascript
const hasWebGPU = !!navigator.gpu;

const session = await ort.InferenceSession.create('fraud_model.onnx', {
  executionProviders: [hasWebGPU ? 'webgpu' : 'wasm']
});

console.log(`Using: ${hasWebGPU ? 'WebGPU (GPU)' : 'WASM (CPU)'}`);
```

### Browser Support for WebGPU

| Browser | Version | Status |
|---------|---------|--------|
| Chrome/Edge | 113+ | ✅ Stable |
| Safari | 18+ | ✅ Stable |
| Chrome Android | 121+ | ✅ Stable |
| Firefox | 141+ | ⚠️ Windows only, flag required |

## Offline Support

Enable offline fraud detection with Service Workers:

```javascript
// service-worker.js
const CACHE_NAME = 'fraudshield-models-v1';
const MODEL_FILES = [
  '/models/fraud_lightgbm.onnx',
  '/models/fraud_lstm.onnx'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(MODEL_FILES))
  );
});

self.addEventListener('fetch', event => {
  if (event.request.url.endsWith('.onnx')) {
    event.respondWith(
      caches.match(event.request)
        .then(response => response || fetch(event.request))
    );
  }
});
```

## Model Conversion

### sklearn to ONNX
```python
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

initial_type = [('float_input', FloatTensorType([None, 15]))]
onnx_model = convert_sklearn(sklearn_model, initial_types=initial_type)

with open("fraud_model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())
```

### TensorFlow to ONNX
```bash
pip install tf2onnx
python -m tf2onnx.convert --saved-model ./saved_model --output fraud_model.onnx
```

### PyTorch to ONNX
```python
import torch.onnx

dummy_input = torch.randn(1, 15)
torch.onnx.export(model, dummy_input, "fraud_model.onnx",
                  input_names=['input'], output_names=['output'])
```

## Performance Optimization

### 1. Quantize to INT8 (4x smaller)
```bash
python -m onnxruntime.quantization.quantize \
  --model fraud_model.onnx \
  --output fraud_model_int8.onnx \
  --per_channel
```

### 2. Enable SIMD & Threads
```javascript
ort.env.wasm.numThreads = navigator.hardwareConcurrency;
ort.env.wasm.simd = true;
```

### 3. Batch Predictions
```javascript
// Process multiple transactions at once
const batchInput = new ort.Tensor('float32', batchFeatures, [batchSize, 15]);
const results = await session.run({ input: batchInput });
```

## Integration with FraudShield MVP

See `browser_integration.html` for a complete example integrating with the FraudShield Uganda MVP.

## Files in this Folder

- `README.md` - This documentation
- `browser_integration.html` - Complete browser example
- `onnx_runtime_example.js` - ONNX Runtime Web usage
- `feature_extraction.js` - Feature engineering for fraud models
- `webgpu_detection.js` - WebGPU capability detection

## Resources

- [ONNX Runtime Web Docs](https://onnxruntime.ai/docs/get-started/with-javascript.html)
- [tract GitHub](https://github.com/sonos/tract)
- [candle WASM Examples](https://github.com/huggingface/candle/tree/main/candle-wasm-examples)
- [TensorFlow.js WebGPU](https://www.tensorflow.org/js/guide/platform_environment)

## Support

- **Email**: sseguya256@gmail.com
- **Website**: [fraudshield-uganda.vercel.app](https://fraudshield-uganda.vercel.app)
