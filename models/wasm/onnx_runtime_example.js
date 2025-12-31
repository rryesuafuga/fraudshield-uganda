/**
 * FraudShield Uganda - ONNX Runtime Web Integration
 *
 * Complete example of loading and running fraud detection models
 * in the browser using ONNX Runtime Web.
 */

// Import ONNX Runtime (use CDN or npm)
// CDN: <script src="https://cdn.jsdelivr.net/npm/onnxruntime-web/dist/ort.min.js"></script>
// NPM: import * as ort from 'onnxruntime-web';

/**
 * FraudDetector class for browser-based ML inference.
 */
class FraudDetector {
    constructor(options = {}) {
        this.session = null;
        this.modelLoaded = false;
        this.backend = options.backend || 'auto';
        this.threshold = options.threshold || 0.5;
        this.modelUrl = options.modelUrl || null;
    }

    /**
     * Detect best available execution provider.
     * @returns {Promise<string>} - 'webgpu', 'webgl', or 'wasm'
     */
    async detectBackend() {
        if (this.backend !== 'auto') {
            return this.backend;
        }

        // Check WebGPU support
        if (typeof navigator !== 'undefined' && navigator.gpu) {
            try {
                const adapter = await navigator.gpu.requestAdapter();
                if (adapter) {
                    console.log('WebGPU available');
                    return 'webgpu';
                }
            } catch (e) {
                console.log('WebGPU check failed:', e);
            }
        }

        // Fall back to WASM (most compatible)
        console.log('Using WASM backend');
        return 'wasm';
    }

    /**
     * Load ONNX model from URL or file.
     * @param {string|ArrayBuffer} modelSource - URL or model bytes
     * @returns {Promise<boolean>} - Success status
     */
    async loadModel(modelSource) {
        try {
            const backend = await this.detectBackend();

            // Configure ONNX Runtime
            if (typeof ort !== 'undefined') {
                ort.env.wasm.numThreads = navigator.hardwareConcurrency || 4;
                ort.env.wasm.simd = true;
            }

            const options = {
                executionProviders: [backend],
                graphOptimizationLevel: 'all',
            };

            // Load model
            if (typeof modelSource === 'string') {
                this.session = await ort.InferenceSession.create(modelSource, options);
            } else {
                this.session = await ort.InferenceSession.create(modelSource, options);
            }

            this.modelLoaded = true;
            console.log(`Model loaded with ${backend} backend`);

            // Log model info
            console.log('Input names:', this.session.inputNames);
            console.log('Output names:', this.session.outputNames);

            return true;
        } catch (error) {
            console.error('Failed to load model:', error);
            this.modelLoaded = false;
            return false;
        }
    }

    /**
     * Run fraud detection on a single transaction.
     * @param {Float32Array} features - Feature vector (length 15)
     * @returns {Promise<Object>} - Prediction result
     */
    async predict(features) {
        if (!this.modelLoaded) {
            throw new Error('Model not loaded. Call loadModel() first.');
        }

        const startTime = performance.now();

        // Create input tensor
        const inputName = this.session.inputNames[0];
        const input = new ort.Tensor('float32', features, [1, features.length]);

        // Run inference
        const feeds = { [inputName]: input };
        const results = await this.session.run(feeds);

        // Get output
        const outputName = this.session.outputNames[0];
        const output = results[outputName];
        const score = output.data[0];

        const endTime = performance.now();

        return {
            score: score,
            isFraud: score > this.threshold,
            riskLevel: this.getRiskLevel(score),
            confidence: this.getConfidence(score),
            inferenceTime: endTime - startTime,
        };
    }

    /**
     * Run fraud detection on multiple transactions (batch).
     * @param {Float32Array} batchFeatures - Batched features
     * @param {number} batchSize - Number of transactions
     * @param {number} featureCount - Features per transaction
     * @returns {Promise<Array>} - Array of prediction results
     */
    async predictBatch(batchFeatures, batchSize, featureCount = 15) {
        if (!this.modelLoaded) {
            throw new Error('Model not loaded. Call loadModel() first.');
        }

        const startTime = performance.now();

        // Create input tensor
        const inputName = this.session.inputNames[0];
        const input = new ort.Tensor('float32', batchFeatures, [batchSize, featureCount]);

        // Run inference
        const feeds = { [inputName]: input };
        const results = await this.session.run(feeds);

        // Get output
        const outputName = this.session.outputNames[0];
        const output = results[outputName];

        const endTime = performance.now();

        // Parse results
        const predictions = [];
        for (let i = 0; i < batchSize; i++) {
            const score = output.data[i];
            predictions.push({
                score: score,
                isFraud: score > this.threshold,
                riskLevel: this.getRiskLevel(score),
            });
        }

        return {
            predictions: predictions,
            totalTime: endTime - startTime,
            avgTime: (endTime - startTime) / batchSize,
        };
    }

    /**
     * Get risk level from score.
     * @param {number} score - Fraud probability (0-1)
     * @returns {string} - 'LOW', 'MEDIUM', or 'HIGH'
     */
    getRiskLevel(score) {
        if (score >= 0.7) return 'HIGH';
        if (score >= 0.4) return 'MEDIUM';
        return 'LOW';
    }

    /**
     * Get confidence level from score.
     * @param {number} score - Fraud probability (0-1)
     * @returns {string} - Confidence description
     */
    getConfidence(score) {
        const distance = Math.abs(score - 0.5);
        if (distance > 0.4) return 'Very High';
        if (distance > 0.25) return 'High';
        if (distance > 0.1) return 'Medium';
        return 'Low';
    }

    /**
     * Get model information.
     * @returns {Object} - Model metadata
     */
    getModelInfo() {
        if (!this.modelLoaded) {
            return { loaded: false };
        }

        return {
            loaded: true,
            inputNames: this.session.inputNames,
            outputNames: this.session.outputNames,
            threshold: this.threshold,
        };
    }

    /**
     * Run performance benchmark.
     * @param {Float32Array} features - Sample features
     * @param {number} iterations - Number of iterations
     * @returns {Promise<Object>} - Benchmark results
     */
    async benchmark(features, iterations = 100) {
        if (!this.modelLoaded) {
            throw new Error('Model not loaded. Call loadModel() first.');
        }

        const times = [];

        // Warm up
        for (let i = 0; i < 5; i++) {
            await this.predict(features);
        }

        // Benchmark
        for (let i = 0; i < iterations; i++) {
            const start = performance.now();
            await this.predict(features);
            times.push(performance.now() - start);
        }

        // Calculate statistics
        times.sort((a, b) => a - b);
        const sum = times.reduce((a, b) => a + b, 0);

        return {
            iterations: iterations,
            totalTime: sum,
            avgTime: sum / iterations,
            minTime: times[0],
            maxTime: times[times.length - 1],
            medianTime: times[Math.floor(iterations / 2)],
            p95Time: times[Math.floor(iterations * 0.95)],
            throughput: (iterations / sum) * 1000, // predictions per second
        };
    }
}

/**
 * Quick usage example.
 */
async function quickExample() {
    // Initialize detector
    const detector = new FraudDetector({
        threshold: 0.5,
    });

    // Load model
    const loaded = await detector.loadModel('fraud_model.onnx');
    if (!loaded) {
        console.error('Failed to load model');
        return;
    }

    // Sample transaction features
    const features = new Float32Array([
        500000,   // amount
        1.2,      // amount ratio
        14,       // hour
        2,        // day of week
        0,        // is weekend
        0,        // after hours
        365,      // customer age
        15,       // tx count 30d
        400000,   // avg amount 30d
        0.2,      // merchant category
        1,        // same device
        0,        // distance
        60,       // minutes since prev
        0,        // failed attempts
        5,        // unique merchants
    ]);

    // Run prediction
    const result = await detector.predict(features);
    console.log('Prediction:', result);

    // Run benchmark
    const benchmark = await detector.benchmark(features, 100);
    console.log('Benchmark:', benchmark);
}

// Export for use as module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FraudDetector };
}

// Export for ES modules
export { FraudDetector };
export default FraudDetector;
