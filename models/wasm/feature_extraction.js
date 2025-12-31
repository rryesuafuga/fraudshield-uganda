/**
 * FraudShield Uganda - Feature Extraction for ML Models
 *
 * Converts raw transaction data into feature vectors for ONNX models.
 * Compatible with Hazelcast, IBM, and custom fraud detection models.
 */

/**
 * Standard 15-feature extraction for fraud detection models.
 *
 * @param {Object} transaction - Transaction data
 * @param {Object} customerHistory - Customer historical data
 * @returns {Float32Array} - Feature vector of length 15
 */
export function extractFeatures(transaction, customerHistory = {}) {
    const features = new Float32Array(15);

    // Feature 0: Transaction amount
    features[0] = parseFloat(transaction.amount) || 0;

    // Feature 1: Amount ratio to customer average
    const avgAmount = customerHistory.avgAmount30d || transaction.amount;
    features[1] = features[0] / (avgAmount || 1);

    // Feature 2: Hour of day (0-23)
    features[2] = extractHour(transaction.time || transaction.approval_time);

    // Feature 3: Day of week (0-6, Monday=0)
    features[3] = extractDayOfWeek(transaction.date || transaction.loan_date);

    // Feature 4: Is weekend (0 or 1)
    features[4] = features[3] >= 5 ? 1 : 0;

    // Feature 5: After business hours (0 or 1)
    features[5] = (features[2] < 8 || features[2] >= 18) ? 1 : 0;

    // Feature 6: Customer age in days
    features[6] = customerHistory.customerAgeDays || 365;

    // Feature 7: Transaction count last 30 days
    features[7] = customerHistory.transactionCount30d || 10;

    // Feature 8: Average amount last 30 days
    features[8] = customerHistory.avgAmount30d || features[0];

    // Feature 9: Merchant category code (normalized)
    features[9] = normalizeMerchantCategory(transaction.merchantCategory);

    // Feature 10: Same device as previous transaction (0 or 1)
    features[10] = transaction.sameDevice ? 1 : 0;

    // Feature 11: Distance from previous transaction (km)
    features[11] = transaction.distanceFromPrev || 0;

    // Feature 12: Minutes since previous transaction
    features[12] = transaction.minutesSincePrev || 60;

    // Feature 13: Failed attempts in last 24 hours
    features[13] = customerHistory.failedAttempts24h || 0;

    // Feature 14: Unique merchants in last 7 days
    features[14] = customerHistory.uniqueMerchants7d || 5;

    return features;
}

/**
 * Extract features for IBM LSTM model (sequence-based).
 * Expects 7 transactions with 220 features each.
 *
 * @param {Array} transactionSequence - Array of 7 transactions
 * @returns {Float32Array} - Feature tensor of shape (7, 16, 220)
 */
export function extractLSTMFeatures(transactionSequence) {
    const seqLength = 7;
    const features = new Float32Array(seqLength * 16 * 220);

    // Pad sequence if less than 7 transactions
    while (transactionSequence.length < seqLength) {
        transactionSequence.unshift(createEmptyTransaction());
    }

    // Take last 7 transactions
    const sequence = transactionSequence.slice(-seqLength);

    for (let i = 0; i < seqLength; i++) {
        const tx = sequence[i];
        const baseIdx = i * 16 * 220;

        // Basic features (first 15)
        const basicFeatures = extractFeatures(tx);
        for (let j = 0; j < 15; j++) {
            features[baseIdx + j] = basicFeatures[j];
        }

        // Additional features would be added here
        // (merchant embeddings, customer embeddings, etc.)
    }

    return features;
}

/**
 * Extract hour from time string.
 * @param {string} timeStr - Time string (HH:MM or HH:MM:SS)
 * @returns {number} - Hour (0-23)
 */
function extractHour(timeStr) {
    if (!timeStr) return 12; // Default to noon

    const str = String(timeStr);
    const match = str.match(/(\d{1,2}):(\d{2})/);
    if (match) {
        return parseInt(match[1], 10);
    }
    return 12;
}

/**
 * Extract day of week from date string.
 * @param {string} dateStr - Date string (YYYY-MM-DD or similar)
 * @returns {number} - Day of week (0=Monday, 6=Sunday)
 */
function extractDayOfWeek(dateStr) {
    if (!dateStr) return 2; // Default to Wednesday

    try {
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) return 2;
        // JavaScript: 0=Sunday, convert to 0=Monday
        const day = date.getDay();
        return day === 0 ? 6 : day - 1;
    } catch {
        return 2;
    }
}

/**
 * Normalize merchant category code.
 * @param {string|number} category - Merchant category
 * @returns {number} - Normalized category (0-1)
 */
function normalizeMerchantCategory(category) {
    const categoryMap = {
        'retail': 0.1,
        'grocery': 0.15,
        'restaurant': 0.2,
        'gas': 0.25,
        'travel': 0.4,
        'entertainment': 0.35,
        'utilities': 0.1,
        'healthcare': 0.15,
        'education': 0.1,
        'transfer': 0.5,
        'withdrawal': 0.45,
        'online': 0.55,
        'foreign': 0.7,
        'gambling': 0.8,
        'crypto': 0.75,
    };

    if (typeof category === 'number') {
        return Math.min(category / 10000, 1); // MCC code normalization
    }

    const key = String(category).toLowerCase();
    return categoryMap[key] || 0.3;
}

/**
 * Create empty transaction for padding.
 * @returns {Object} - Empty transaction object
 */
function createEmptyTransaction() {
    return {
        amount: 0,
        time: '12:00',
        date: new Date().toISOString().split('T')[0],
        merchantCategory: 'unknown',
        sameDevice: true,
        distanceFromPrev: 0,
        minutesSincePrev: 0,
    };
}

/**
 * Batch extract features for multiple transactions.
 * @param {Array} transactions - Array of transaction objects
 * @param {Object} customerHistory - Customer historical data
 * @returns {Float32Array} - Batched feature tensor
 */
export function extractBatchFeatures(transactions, customerHistory = {}) {
    const batchSize = transactions.length;
    const featureCount = 15;
    const features = new Float32Array(batchSize * featureCount);

    for (let i = 0; i < batchSize; i++) {
        const txFeatures = extractFeatures(transactions[i], customerHistory);
        features.set(txFeatures, i * featureCount);
    }

    return features;
}

/**
 * Normalize features for model input.
 * Apply z-score normalization based on training statistics.
 *
 * @param {Float32Array} features - Raw features
 * @param {Object} stats - Mean and std for each feature
 * @returns {Float32Array} - Normalized features
 */
export function normalizeFeatures(features, stats = DEFAULT_STATS) {
    const normalized = new Float32Array(features.length);

    for (let i = 0; i < features.length; i++) {
        const featureIdx = i % 15;
        const mean = stats.means[featureIdx] || 0;
        const std = stats.stds[featureIdx] || 1;
        normalized[i] = (features[i] - mean) / std;
    }

    return normalized;
}

// Default normalization statistics (from training data)
const DEFAULT_STATS = {
    means: [500000, 1.0, 12, 2.5, 0.28, 0.25, 365, 15, 500000, 0.3, 0.8, 5, 60, 0.1, 5],
    stds: [1000000, 2.0, 6, 2, 0.45, 0.43, 300, 10, 800000, 0.25, 0.4, 20, 120, 0.5, 4],
};

export default {
    extractFeatures,
    extractLSTMFeatures,
    extractBatchFeatures,
    normalizeFeatures,
};
