/**
 * FraudShield Uganda - WebAssembly MVP
 * JavaScript wrapper for Rust/Wasm fraud detection engine
 */

// ============================================
// GLOBAL STATE
// ============================================
let wasmModule = null;
let rawData = [];
let columnMappings = [];
let analysisResults = null;
let currentStep = 1;

// Standard field definitions for display
const STANDARD_FIELDS = {
    loan_id: { description: 'Loan ID', required: true },
    borrower_id: { description: 'Borrower/Member ID', required: true },
    borrower_name: { description: 'Borrower Name', required: false },
    phone: { description: 'Phone Number', required: true },
    national_id: { description: 'National ID (NIN)', required: false },
    amount: { description: 'Loan Amount', required: true },
    loan_date: { description: 'Loan Date', required: false },
    approval_time: { description: 'Approval Time', required: false },
    officer_id: { description: 'Officer ID', required: true },
    officer_name: { description: 'Officer Name', required: false },
    branch: { description: 'Branch', required: false },
    status: { description: 'Status', required: false },
    guarantor_name: { description: 'Guarantor Name', required: false },
    guarantor_phone: { description: 'Guarantor Phone', required: false },
    interest_rate: { description: 'Interest Rate', required: false },
    term_months: { description: 'Term (Months)', required: false },
    purpose: { description: 'Loan Purpose', required: false },
    address: { description: 'Address', required: false }
};

// Method labels for display
const METHOD_LABELS = {
    'exact_match': { label: 'Exact', color: 'emerald', icon: '✓' },
    'name_match': { label: 'Name', color: 'emerald', icon: '≈' },
    'fuzzy_match': { label: 'Fuzzy', color: 'blue', icon: '~' },
    'pattern': { label: 'Pattern', color: 'purple', icon: '⬡' },
    'statistics': { label: 'Stats', color: 'cyan', icon: '📊' },
    'manual': { label: 'Manual', color: 'slate', icon: '✎' },
    'none': { label: '-', color: 'slate', icon: '-' }
};

// ============================================
// WASM INITIALIZATION
// ============================================
async function initWasm() {
    try {
        // Import the wasm module
        wasmModule = await import('../pkg/fraudshield_wasm.js');
        await wasmModule.default();

        console.log('✅ FraudShield Wasm module loaded successfully');
        updateWasmStatus(true);
        return true;
    } catch (error) {
        console.error('❌ Failed to load Wasm module:', error);
        updateWasmStatus(false);

        // Fall back to JavaScript implementation
        console.log('⚠️ Using JavaScript fallback mode');
        return false;
    }
}

function updateWasmStatus(loaded) {
    const statusEl = document.getElementById('wasm-status');
    if (statusEl) {
        if (loaded) {
            statusEl.innerHTML = `
                <span class="w-2 h-2 bg-emerald-400 rounded-full pulse-dot"></span>
                <span class="text-emerald-400 text-xs font-medium">Wasm Active</span>
            `;
        } else {
            statusEl.innerHTML = `
                <span class="w-2 h-2 bg-amber-400 rounded-full"></span>
                <span class="text-amber-400 text-xs font-medium">JS Fallback</span>
            `;
        }
    }
}

// ============================================
// FILE HANDLING
// ============================================
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    const extension = file.name.split('.').pop().toLowerCase();

    showLoading('Reading file...');

    if (extension === 'csv') {
        reader.onload = (e) => {
            if (wasmModule) {
                // Use Wasm CSV parser
                const jsonStr = wasmModule.parse_csv(e.target.result);
                rawData = JSON.parse(jsonStr);
            } else {
                // Fallback: Use PapaParse
                Papa.parse(e.target.result, {
                    header: true,
                    skipEmptyLines: true,
                    complete: (results) => {
                        rawData = results.data;
                    }
                });
            }
            processUploadedData();
        };
        reader.readAsText(file);
    } else if (extension === 'xlsx' || extension === 'xls') {
        reader.onload = (e) => {
            const workbook = XLSX.read(e.target.result, { type: 'binary' });
            const sheetName = workbook.SheetNames[0];
            const sheet = workbook.Sheets[sheetName];
            rawData = XLSX.utils.sheet_to_json(sheet);
            processUploadedData();
        };
        reader.readAsBinaryString(file);
    }
}

function loadSampleData() {
    showLoading('Generating sample data...');

    setTimeout(() => {
        if (wasmModule) {
            // Use Wasm sample data generator
            const jsonStr = wasmModule.generate_sample_data(500);
            rawData = JSON.parse(jsonStr);
        } else {
            // Fallback: Generate in JavaScript
            rawData = generateSampleDataJS(500);
        }
        processUploadedData();
    }, 100);
}

function generateSampleDataJS(numLoans) {
    // JavaScript fallback for sample data generation
    const firstNames = ['John', 'Mary', 'Peter', 'Grace', 'David', 'Sarah', 'James', 'Agnes', 'Robert', 'Florence'];
    const lastNames = ['Mukasa', 'Nakato', 'Ssemakula', 'Nambi', 'Okello', 'Akello', 'Wasswa', 'Babirye', 'Kato', 'Nalongo'];
    const officers = ['OFF001', 'OFF002', 'OFF003', 'OFF004', 'OFF005'];
    const branches = ['Kampala Central', 'Entebbe', 'Jinja', 'Mbarara', 'Gulu'];
    const statuses = ['active', 'active', 'active', 'completed', 'defaulted'];

    const data = [];
    const fraudPhones = [];

    for (let i = 0; i < 5; i++) {
        fraudPhones.push('07' + Math.floor(Math.random() * 90000000 + 10000000));
    }

    for (let i = 0; i < numLoans; i++) {
        const isFraud = Math.random() < 0.05;
        const isGhostLoan = isFraud && Math.random() < 0.5;
        const isStacking = isFraud && !isGhostLoan && Math.random() < 0.5;

        const hour = isFraud && !isGhostLoan && !isStacking ?
            (Math.random() < 0.5 ? Math.floor(Math.random() * 5) : Math.floor(Math.random() * 3) + 22) :
            Math.floor(Math.random() * 10) + 8;

        data.push({
            loan_id: `LN${String(i + 1).padStart(5, '0')}`,
            borrower_id: isStacking ? `MBR${String(Math.floor(i / 3)).padStart(4, '0')}` : `MBR${String(i + 1).padStart(4, '0')}`,
            borrower_name: `${firstNames[Math.floor(Math.random() * firstNames.length)]} ${lastNames[Math.floor(Math.random() * lastNames.length)]}`,
            phone: isGhostLoan ? fraudPhones[Math.floor(Math.random() * fraudPhones.length)] : '07' + Math.floor(Math.random() * 90000000 + 10000000),
            amount: Math.floor(Math.random() * 4000000 + 500000),
            loan_date: `2024-${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}-${String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')}`,
            approval_time: `${String(hour).padStart(2, '0')}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}`,
            officer_id: isFraud ? officers[0] : officers[Math.floor(Math.random() * officers.length)],
            branch: branches[Math.floor(Math.random() * branches.length)],
            status: statuses[Math.floor(Math.random() * statuses.length)]
        });
    }

    return data;
}

// ============================================
// DATA PROCESSING
// ============================================
function processUploadedData() {
    if (!rawData || rawData.length === 0) {
        hideLoading();
        return;
    }

    showLoading('Detecting columns...');

    setTimeout(() => {
        // Detect column mappings
        if (wasmModule) {
            const jsonStr = wasmModule.detect_columns(JSON.stringify(rawData));
            columnMappings = JSON.parse(jsonStr);
        } else {
            // Fallback: Basic column matching
            columnMappings = detectColumnsJS(rawData);
        }

        hideLoading();
        goToStep(2);
        renderMappingTable();
        renderDataPreview();
    }, 100);
}

function detectColumnsJS(data) {
    // JavaScript fallback for column detection
    const columns = Object.keys(data[0] || {});
    const mappings = [];

    const nameVariations = {
        loan_id: ['loan_id', 'loanid', 'loan_no', 'id', 'ref_no'],
        borrower_id: ['borrower_id', 'member_id', 'client_id', 'account_no'],
        borrower_name: ['borrower_name', 'name', 'full_name', 'member_name'],
        phone: ['phone', 'mobile', 'telephone', 'contact'],
        amount: ['amount', 'loan_amount', 'principal'],
        loan_date: ['loan_date', 'date', 'disbursement_date'],
        approval_time: ['approval_time', 'time', 'timestamp'],
        officer_id: ['officer_id', 'staff_id', 'approved_by'],
        branch: ['branch', 'location', 'office'],
        status: ['status', 'loan_status', 'state']
    };

    const usedFields = new Set();

    columns.forEach(col => {
        const colLower = col.toLowerCase().replace(/[^a-z0-9]/g, '_');
        let matched = false;

        for (const [field, variations] of Object.entries(nameVariations)) {
            if (usedFields.has(field)) continue;

            for (const variation of variations) {
                if (colLower === variation || colLower.includes(variation)) {
                    mappings.push({
                        original_column: col,
                        mapped_field: field,
                        confidence: colLower === variation ? 100 : 85,
                        detection_method: 'name_match'
                    });
                    usedFields.add(field);
                    matched = true;
                    break;
                }
            }
            if (matched) break;
        }

        if (!matched) {
            mappings.push({
                original_column: col,
                mapped_field: null,
                confidence: 0,
                detection_method: 'none'
            });
        }
    });

    return mappings;
}

// ============================================
// MAPPING UI
// ============================================
function renderMappingTable() {
    const container = document.getElementById('mapping-table');

    let mapped = columnMappings.filter(m => m.mapped_field).length;
    let html = '<table class="w-full text-sm"><thead><tr class="text-left text-slate-400 border-b border-slate-700">' +
        '<th class="pb-2 pr-4">Original Column</th>' +
        '<th class="pb-2 pr-4">Detected As</th>' +
        '<th class="pb-2 pr-4">Confidence</th>' +
        '<th class="pb-2 pr-4">Method</th>' +
        '<th class="pb-2">Sample Values</th></tr></thead><tbody>';

    columnMappings.forEach((mapping, idx) => {
        const col = mapping.original_column;
        const sample = rawData.slice(0, 5).map(r => r[col]).filter(v => v !== undefined && v !== null && v !== '').slice(0, 4);

        if (mapping.mapped_field) {
            const confColor = mapping.confidence >= 80 ? 'emerald' : mapping.confidence >= 60 ? 'amber' : 'red';
            const methodInfo = METHOD_LABELS[mapping.detection_method] || METHOD_LABELS.none;

            html += `<tr class="border-b border-slate-800">
                <td class="py-2 pr-4 font-mono text-slate-300">${col}</td>
                <td class="py-2 pr-4">
                    <select class="bg-slate-700 rounded px-2 py-1 text-sm border-none" onchange="updateMapping(${idx}, this.value)">
                        ${Object.keys(STANDARD_FIELDS).map(f =>
                            `<option value="${f}" ${f === mapping.mapped_field ? 'selected' : ''}>${f}</option>`
                        ).join('')}
                        <option value="">-- Skip --</option>
                    </select>
                </td>
                <td class="py-2 pr-4">
                    <div class="flex items-center space-x-2">
                        <div class="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                            <div class="h-full bg-${confColor}-500 confidence-bar" style="width: ${mapping.confidence}%"></div>
                        </div>
                        <span class="text-xs text-${confColor}-400">${mapping.confidence}%</span>
                    </div>
                </td>
                <td class="py-2 pr-4">
                    <span class="px-2 py-0.5 text-xs rounded bg-${methodInfo.color}-500/20 text-${methodInfo.color}-400">
                        ${methodInfo.icon} ${methodInfo.label}
                    </span>
                </td>
                <td class="py-2 text-xs text-slate-500 truncate max-w-xs" title="${sample.join(', ')}">${sample.join(', ')}</td>
            </tr>`;
        } else {
            html += `<tr class="border-b border-slate-800 bg-slate-800/30">
                <td class="py-2 pr-4 font-mono text-slate-500">${col}</td>
                <td class="py-2 pr-4">
                    <select class="bg-slate-700 rounded px-2 py-1 text-sm border-none" onchange="updateMapping(${idx}, this.value)">
                        <option value="">-- Not Detected --</option>
                        ${Object.keys(STANDARD_FIELDS).map(f =>
                            `<option value="${f}">${f}</option>`
                        ).join('')}
                    </select>
                </td>
                <td class="py-2 pr-4 text-xs text-slate-500">-</td>
                <td class="py-2 pr-4 text-xs text-slate-500">-</td>
                <td class="py-2 text-xs text-slate-500 truncate max-w-xs" title="${sample.join(', ')}">${sample.join(', ')}</td>
            </tr>`;
        }
    });

    html += '</tbody></table>';
    container.innerHTML = html;

    document.getElementById('mapping-summary').textContent =
        `${mapped} of ${columnMappings.length} columns auto-detected`;
}

function renderDataPreview() {
    const container = document.getElementById('data-preview');
    const columns = Object.keys(rawData[0] || {});
    const preview = rawData.slice(0, 10);

    let html = '<table class="w-full text-xs"><thead><tr class="text-left text-slate-400">';
    columns.forEach(col => {
        html += `<th class="pb-2 pr-4 whitespace-nowrap">${col}</th>`;
    });
    html += '</tr></thead><tbody>';

    preview.forEach(row => {
        html += '<tr class="border-b border-slate-800">';
        columns.forEach(col => {
            html += `<td class="py-2 pr-4 whitespace-nowrap text-slate-300">${row[col] || ''}</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

function updateMapping(idx, newField) {
    if (newField) {
        columnMappings[idx].mapped_field = newField;
        columnMappings[idx].confidence = 100;
        columnMappings[idx].detection_method = 'manual';
    } else {
        columnMappings[idx].mapped_field = null;
        columnMappings[idx].confidence = 0;
    }
    renderMappingTable();
}

// ============================================
// FRAUD ANALYSIS
// ============================================
function proceedToAnalysis() {
    goToStep(3);
    runFraudAnalysis();
}

async function runFraudAnalysis() {
    // Build mapped data
    const mappedData = rawData.map(row => {
        const mapped = {};
        columnMappings.forEach(mapping => {
            if (mapping.mapped_field) {
                let value = row[mapping.original_column];
                // Convert amount to number if it's the amount field
                if (mapping.mapped_field === 'amount' && typeof value === 'string') {
                    value = parseFloat(value.replace(/,/g, '')) || 0;
                }
                mapped[mapping.mapped_field] = value;
            }
        });
        return mapped;
    });

    // Animate progress
    const checks = ['check-ghost', 'check-stacking', 'check-officer', 'check-timing', 'check-amount'];
    for (const checkId of checks) {
        await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 200));
        const el = document.getElementById(checkId);
        if (el) {
            el.innerHTML = `<i data-lucide="check-circle" class="h-4 w-4 inline text-emerald-400 mr-2"></i>${el.textContent.replace('...', ' - Complete')}`;
            lucide.createIcons();
        }
    }

    // Run analysis
    setTimeout(() => {
        if (wasmModule) {
            const jsonStr = wasmModule.analyze_fraud(JSON.stringify(mappedData));
            analysisResults = JSON.parse(jsonStr);
        } else {
            // Fallback: Basic fraud detection in JavaScript
            analysisResults = analyzeeFraudJS(mappedData);
        }

        goToStep(4);
        renderResults();
    }, 500);
}

function analyzeeFraudJS(data) {
    // JavaScript fallback for fraud analysis
    const alerts = [];
    const officers = {};

    // Ghost loan detection
    const phoneCounts = {};
    data.forEach((row, idx) => {
        const phone = row.phone;
        if (phone) {
            if (!phoneCounts[phone]) phoneCounts[phone] = [];
            phoneCounts[phone].push(row);
        }
    });

    Object.entries(phoneCounts).forEach(([phone, rows]) => {
        if (rows.length > 1) {
            const totalAmount = rows.reduce((sum, r) => sum + (parseFloat(r.amount) || 0), 0);
            alerts.push({
                alert_type: 'GHOST_LOAN',
                severity: rows.length >= 4 ? 'CRITICAL' : 'HIGH',
                title: 'Duplicate Phone Number Detected',
                description: `Phone ${phone} appears in ${rows.length} different loans`,
                amount_at_risk: totalAmount,
                officer_id: rows[0].officer_id,
                loan_ids: rows.map(r => r.loan_id).filter(Boolean),
                details: rows
            });
        }
    });

    // Officer statistics
    data.forEach(row => {
        const officerId = row.officer_id || 'Unknown';
        if (!officers[officerId]) {
            officers[officerId] = {
                officer_id: officerId,
                name: row.officer_name || officerId,
                loan_count: 0,
                total_amount: 0,
                alert_count: 0,
                z_score: 0,
                risk_score: 0
            };
        }
        officers[officerId].loan_count++;
        officers[officerId].total_amount += parseFloat(row.amount) || 0;
    });

    // Calculate summary
    const summary = {
        total_records: data.length,
        critical_alerts: alerts.filter(a => a.severity === 'CRITICAL').length,
        high_alerts: alerts.filter(a => a.severity === 'HIGH').length,
        medium_alerts: alerts.filter(a => a.severity === 'MEDIUM').length,
        low_alerts: alerts.filter(a => a.severity === 'LOW').length,
        risk_score: Math.min(100, alerts.length * 10)
    };

    return {
        summary,
        alerts,
        officers: Object.values(officers)
    };
}

// ============================================
// RESULTS UI
// ============================================
function renderResults() {
    const summary = analysisResults.summary;

    // Update summary stats
    document.getElementById('risk-score').textContent = summary.risk_score;
    document.getElementById('risk-bar').style.width = summary.risk_score + '%';

    const riskColor = summary.risk_score >= 70 ? 'bg-red-500' :
                      summary.risk_score >= 40 ? 'bg-orange-500' :
                      summary.risk_score >= 20 ? 'bg-yellow-500' : 'bg-emerald-500';
    document.getElementById('risk-bar').className = `h-full ${riskColor} rounded-full confidence-bar`;
    document.getElementById('risk-score').className = `text-3xl font-bold ${riskColor.replace('bg-', 'text-')}`;

    document.getElementById('total-records').textContent = summary.total_records.toLocaleString();
    document.getElementById('critical-count').textContent = summary.critical_alerts;
    document.getElementById('high-count').textContent = summary.high_alerts;
    document.getElementById('medium-count').textContent = summary.medium_alerts;

    renderAlerts('all');
    renderOfficers();
    renderDataTable();

    lucide.createIcons();
}

function renderAlerts(filter) {
    const container = document.getElementById('alerts-list');
    let alerts = analysisResults.alerts;

    if (filter !== 'all') {
        alerts = alerts.filter(a => a.severity === filter);
    }

    if (alerts.length === 0) {
        container.innerHTML = '<div class="p-8 text-center text-slate-500"><i data-lucide="check-circle" class="h-12 w-12 mx-auto mb-3 text-emerald-500/50"></i><p>No alerts found</p></div>';
        lucide.createIcons();
        return;
    }

    container.innerHTML = alerts.map((alert, idx) => {
        const severityColors = {
            CRITICAL: { bg: 'red-500/10', border: 'red-500/30', text: 'red-400', icon: 'red-500' },
            HIGH: { bg: 'orange-500/10', border: 'orange-500/30', text: 'orange-400', icon: 'orange-500' },
            MEDIUM: { bg: 'yellow-500/10', border: 'yellow-500/30', text: 'yellow-400', icon: 'yellow-500' },
            LOW: { bg: 'blue-500/10', border: 'blue-500/30', text: 'blue-400', icon: 'blue-500' }
        };
        const colors = severityColors[alert.severity] || severityColors.MEDIUM;

        return `<div class="alert-row px-4 py-3 border-b border-slate-700/50 bg-${colors.bg}" onclick="toggleAlertDetails(${idx})">
            <div class="flex items-start space-x-3">
                <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-${colors.icon}/20">
                    <i data-lucide="alert-triangle" class="h-4 w-4 text-${colors.icon}"></i>
                </div>
                <div class="flex-1 min-w-0">
                    <div class="flex items-center flex-wrap gap-2">
                        <span class="px-2 py-0.5 text-xs font-medium rounded bg-${colors.icon} text-white">${alert.severity}</span>
                        <span class="text-xs text-slate-500 bg-slate-800 px-2 py-0.5 rounded">${alert.alert_type.replace(/_/g, ' ')}</span>
                        <span class="font-medium text-white truncate">${alert.title}</span>
                    </div>
                    <p class="text-sm text-slate-400 mt-1">${alert.description}</p>
                    <div class="flex items-center justify-between mt-2">
                        <span class="text-sm font-semibold text-${colors.text}">${formatCurrency(alert.amount_at_risk)}</span>
                        <span class="text-xs text-slate-500">Officer: ${alert.officer_id || 'N/A'}</span>
                    </div>
                </div>
                <i data-lucide="chevron-right" class="h-5 w-5 text-slate-500"></i>
            </div>
            <div id="alert-details-${idx}" class="hidden mt-3 ml-11 p-3 bg-slate-900/50 rounded-lg text-xs">
                <pre class="text-slate-400 overflow-x-auto">${JSON.stringify(alert.details, null, 2)}</pre>
            </div>
        </div>`;
    }).join('');

    lucide.createIcons();
}

function toggleAlertDetails(idx) {
    const el = document.getElementById(`alert-details-${idx}`);
    el.classList.toggle('hidden');
}

function filterAlerts(filter) {
    document.querySelectorAll('.alert-filter').forEach(btn => {
        btn.className = btn.className.replace('bg-slate-700', '').replace('text-slate-400', '');
        if (btn.textContent.toLowerCase().includes(filter.toLowerCase()) || (filter === 'all' && btn.textContent === 'All')) {
            btn.className += ' bg-slate-700';
        } else {
            btn.className += ' text-slate-400 hover:bg-slate-700';
        }
    });
    renderAlerts(filter);
}

function renderOfficers() {
    const container = document.getElementById('officers-list');
    const officers = analysisResults.officers.sort((a, b) => b.risk_score - a.risk_score);

    container.innerHTML = officers.slice(0, 10).map((officer, idx) => {
        const riskScore = officer.risk_score;
        const riskColor = riskScore > 60 ? 'red' : riskScore > 30 ? 'amber' : 'emerald';

        return `<div class="flex items-center space-x-3">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${idx < 2 ? `bg-${riskColor}-500/20 text-${riskColor}-400` : 'bg-slate-700 text-slate-400'}">
                ${idx + 1}
            </div>
            <div class="flex-1">
                <div class="flex items-center justify-between">
                    <p class="text-sm font-medium">${officer.name}</p>
                    <span class="text-sm font-bold text-${riskColor}-400">${riskScore}</span>
                </div>
                <div class="flex items-center justify-between text-xs text-slate-500 mt-0.5">
                    <span>${officer.loan_count} loans</span>
                    <span>${officer.alert_count} alerts</span>
                </div>
                <div class="h-1.5 bg-slate-700 rounded-full mt-1 overflow-hidden">
                    <div class="h-full bg-${riskColor}-500 rounded-full" style="width: ${riskScore}%"></div>
                </div>
            </div>
        </div>`;
    }).join('');
}

function renderDataTable() {
    const container = document.getElementById('data-table');
    const mappedData = rawData.map(row => {
        const mapped = {};
        columnMappings.forEach(mapping => {
            if (mapping.mapped_field) {
                mapped[mapping.mapped_field] = row[mapping.original_column];
            }
        });
        return mapped;
    });

    const columns = columnMappings.filter(m => m.mapped_field).map(m => m.mapped_field);

    let html = '<table class="w-full text-xs"><thead><tr class="text-left text-slate-400 border-b border-slate-700">';
    columns.forEach(col => {
        html += `<th class="pb-2 pr-4 whitespace-nowrap">${col}</th>`;
    });
    html += '</tr></thead><tbody>';

    mappedData.slice(0, 50).forEach(row => {
        html += '<tr class="border-b border-slate-800/50 hover:bg-slate-800/30">';
        columns.forEach(col => {
            const val = row[col];
            const display = typeof val === 'number' ? val.toLocaleString() : (val || '');
            html += `<td class="py-2 pr-4 whitespace-nowrap text-slate-300">${display}</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table>';
    if (mappedData.length > 50) {
        html += `<p class="text-center text-sm text-slate-500 mt-4">Showing 50 of ${mappedData.length} records</p>`;
    }

    container.innerHTML = html;
}

function showResultTab(tab) {
    document.querySelectorAll('.result-tab-content').forEach(el => el.classList.add('hidden'));
    document.getElementById(`tab-${tab}`).classList.remove('hidden');

    document.querySelectorAll('.result-tab').forEach(btn => {
        btn.className = btn.className.replace('bg-emerald-500/20 text-emerald-400', 'text-slate-400 hover:text-white hover:bg-slate-800');
    });
    document.querySelector(`.result-tab[data-tab="${tab}"]`).className =
        'result-tab px-4 py-2 rounded-lg text-sm font-medium bg-emerald-500/20 text-emerald-400';
}

// ============================================
// NAVIGATION
// ============================================
function goToStep(step) {
    currentStep = step;

    // Update step indicators
    for (let i = 1; i <= 4; i++) {
        const el = document.getElementById(`step${i}`);
        el.className = el.className.replace('active', '').replace('completed', '');
        if (i < step) {
            el.classList.add('completed');
            el.innerHTML = '<i data-lucide="check" class="h-4 w-4"></i>';
        } else if (i === step) {
            el.classList.add('active');
            el.textContent = i;
        } else {
            el.textContent = i;
        }
    }
    lucide.createIcons();

    // Show/hide sections
    document.getElementById('upload-section').classList.toggle('hidden', step !== 1);
    document.getElementById('mapping-section').classList.toggle('hidden', step !== 2);
    document.getElementById('analyzing-section').classList.toggle('hidden', step !== 3);
    document.getElementById('results-section').classList.toggle('hidden', step !== 4);
}

function resetAnalysis() {
    rawData = [];
    columnMappings = [];
    analysisResults = null;
    document.getElementById('file-input').value = '';
    goToStep(1);
}

// ============================================
// UTILITIES
// ============================================
function formatCurrency(amount) {
    return 'UGX ' + Number(amount || 0).toLocaleString();
}

function showLoading(message) {
    const overlay = document.getElementById('loading-overlay');
    const msg = document.getElementById('loading-message');
    if (overlay && msg) {
        msg.textContent = message || 'Loading...';
        overlay.classList.remove('hidden');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}

function downloadResults() {
    if (!analysisResults) return;

    const lines = [];

    // Header section
    lines.push('FraudShield Uganda - Fraud Detection Report (Wasm MVP)');
    lines.push(`Generated: ${new Date().toISOString()}`);
    lines.push(`Risk Score: ${analysisResults.summary.risk_score}/100`);
    lines.push(`Total Records: ${analysisResults.summary.total_records}`);
    lines.push(`Critical Alerts: ${analysisResults.summary.critical_alerts}`);
    lines.push(`High Risk Alerts: ${analysisResults.summary.high_alerts}`);
    lines.push(`Medium Risk Alerts: ${analysisResults.summary.medium_alerts}`);
    lines.push('');

    // Alerts section
    lines.push('=== FRAUD ALERTS ===');
    lines.push('Severity,Type,Title,Description,Amount at Risk (UGX),Officer ID');

    analysisResults.alerts.forEach(alert => {
        const row = [
            alert.severity || '',
            (alert.alert_type || '').replace(/_/g, ' '),
            `"${(alert.title || '').replace(/"/g, '""')}"`,
            `"${(alert.description || '').replace(/"/g, '""')}"`,
            alert.amount_at_risk || 0,
            alert.officer_id || ''
        ];
        lines.push(row.join(','));
    });

    lines.push('');

    // Officer ranking section
    lines.push('=== OFFICER RISK RANKING ===');
    lines.push('Officer ID,Name,Loan Count,Alert Count,Risk Score');

    analysisResults.officers.forEach(officer => {
        const row = [
            officer.officer_id,
            `"${(officer.name || '').replace(/"/g, '""')}"`,
            officer.loan_count || 0,
            officer.alert_count || 0,
            officer.risk_score || 0
        ];
        lines.push(row.join(','));
    });

    const csvContent = lines.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `fraudshield-wasm-report-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize Wasm
    await initWasm();

    // Initialize Lucide icons
    lucide.createIcons();
});

// ============================================
// AUTHENTICATION INTEGRATION
// ============================================
let currentUser = null;

/**
 * Initialize authentication and check user status
 */
async function initAuth() {
    // Wait for supabase.js to load
    if (typeof window.FraudShieldAuth === 'undefined') {
        console.warn('⚠️ Supabase auth module not loaded');
        return null;
    }

    const status = window.FraudShieldAuth.getConfigStatus();

    if (!status.configured) {
        console.log('⚠️ Supabase not configured - running in demo mode');
        updateAuthUI(null);
        return null;
    }

    // Check if user is authenticated
    const { user, error } = await window.FraudShieldAuth.getCurrentUser();

    if (user) {
        currentUser = user;
        updateAuthUI(user);
        console.log('✅ User authenticated:', user.email);
    } else {
        updateAuthUI(null);
    }

    return user;
}

/**
 * Update the UI based on authentication status
 */
function updateAuthUI(user) {
    const authSection = document.getElementById('auth-section');
    if (!authSection) return;

    if (user) {
        // User is logged in - show user menu
        const profile = user.user_metadata || {};
        const displayName = profile.full_name || profile.organization_name || user.email.split('@')[0];

        authSection.innerHTML = `
            <div class="relative" id="user-menu-container">
                <button onclick="toggleUserMenu()" class="flex items-center space-x-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors">
                    <div class="w-7 h-7 bg-emerald-500/20 rounded-full flex items-center justify-center">
                        <span class="text-emerald-400 text-xs font-bold">${displayName.charAt(0).toUpperCase()}</span>
                    </div>
                    <span class="text-sm text-slate-300 hidden md:inline">${displayName}</span>
                    <i data-lucide="chevron-down" class="h-4 w-4 text-slate-400"></i>
                </button>
                <div id="user-menu" class="hidden absolute right-0 mt-2 w-56 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50">
                    <div class="p-3 border-b border-slate-700">
                        <p class="text-sm font-medium text-white">${displayName}</p>
                        <p class="text-xs text-slate-400">${user.email}</p>
                        ${profile.organization_name ? `<p class="text-xs text-emerald-400 mt-1">${profile.organization_name}</p>` : ''}
                    </div>
                    <div class="p-2">
                        <button onclick="showAnalysisHistory()" class="w-full text-left px-3 py-2 text-sm text-slate-300 hover:bg-slate-700 rounded flex items-center space-x-2">
                            <i data-lucide="history" class="h-4 w-4"></i>
                            <span>Analysis History</span>
                        </button>
                        <button onclick="showProfileSettings()" class="w-full text-left px-3 py-2 text-sm text-slate-300 hover:bg-slate-700 rounded flex items-center space-x-2">
                            <i data-lucide="settings" class="h-4 w-4"></i>
                            <span>Settings</span>
                        </button>
                        <hr class="my-2 border-slate-700">
                        <button onclick="handleSignOut()" class="w-full text-left px-3 py-2 text-sm text-red-400 hover:bg-slate-700 rounded flex items-center space-x-2">
                            <i data-lucide="log-out" class="h-4 w-4"></i>
                            <span>Sign Out</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
    } else {
        // User is not logged in - show login button
        authSection.innerHTML = `
            <a href="login.html" class="flex items-center space-x-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded-lg text-sm font-medium transition-colors">
                <i data-lucide="log-in" class="h-4 w-4"></i>
                <span>Sign In</span>
            </a>
        `;
    }

    lucide.createIcons();
}

/**
 * Toggle user dropdown menu
 */
function toggleUserMenu() {
    const menu = document.getElementById('user-menu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

// Close menu when clicking outside
document.addEventListener('click', (e) => {
    const container = document.getElementById('user-menu-container');
    const menu = document.getElementById('user-menu');
    if (container && menu && !container.contains(e.target)) {
        menu.classList.add('hidden');
    }
});

/**
 * Handle user sign out
 */
async function handleSignOut() {
    if (typeof window.FraudShieldAuth !== 'undefined') {
        await window.FraudShieldAuth.signOut();
    }
    currentUser = null;
    window.location.href = 'login.html';
}

/**
 * Show analysis history modal
 */
async function showAnalysisHistory() {
    toggleUserMenu();

    if (typeof window.FraudShieldAuth === 'undefined') return;

    const { data: history, error } = await window.FraudShieldAuth.getAnalysisHistory(10);

    if (error) {
        console.error('Failed to load history:', error);
        return;
    }

    // Create and show modal
    const modal = document.createElement('div');
    modal.id = 'history-modal';
    modal.className = 'fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-50 flex items-center justify-center p-4';

    modal.innerHTML = `
        <div class="bg-slate-800 border border-slate-700 rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
            <div class="p-4 border-b border-slate-700 flex items-center justify-between">
                <h3 class="text-lg font-semibold text-white">Analysis History</h3>
                <button onclick="closeHistoryModal()" class="text-slate-400 hover:text-white">
                    <i data-lucide="x" class="h-5 w-5"></i>
                </button>
            </div>
            <div class="p-4 overflow-y-auto max-h-[60vh]">
                ${history.length === 0 ? `
                    <div class="text-center py-8 text-slate-500">
                        <i data-lucide="file-search" class="h-12 w-12 mx-auto mb-3 opacity-50"></i>
                        <p>No analysis history yet</p>
                    </div>
                ` : history.map(item => `
                    <div class="p-3 bg-slate-900/50 rounded-lg mb-3">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-sm font-medium text-white">${item.file_name}</span>
                            <span class="text-xs text-slate-500">${new Date(item.created_at).toLocaleDateString()}</span>
                        </div>
                        <div class="grid grid-cols-3 gap-2 text-xs">
                            <div class="text-slate-400">Records: <span class="text-white">${item.loans_analyzed}</span></div>
                            <div class="text-slate-400">Alerts: <span class="text-amber-400">${item.alerts_generated}</span></div>
                            <div class="text-slate-400">Risk: <span class="${item.risk_score > 50 ? 'text-red-400' : 'text-emerald-400'}">${item.risk_score}</span></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    lucide.createIcons();
}

function closeHistoryModal() {
    const modal = document.getElementById('history-modal');
    if (modal) modal.remove();
}

/**
 * Show profile settings modal
 */
function showProfileSettings() {
    toggleUserMenu();
    // TODO: Implement profile settings modal
    alert('Profile settings coming soon!');
}

/**
 * Save analysis results to database (if authenticated)
 */
async function saveAnalysisToCloud(results, fileName = 'Unknown') {
    if (!currentUser || typeof window.FraudShieldAuth === 'undefined') {
        console.log('Not authenticated, skipping cloud save');
        return;
    }

    const { data, error } = await window.FraudShieldAuth.saveAnalysisSession({
        ...results,
        fileName
    });

    if (error) {
        console.error('Failed to save analysis:', error);
    } else {
        console.log('✅ Analysis saved to cloud');
    }
}

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize Wasm
    await initWasm();

    // Initialize Auth (after a small delay to ensure supabase.js is loaded)
    setTimeout(async () => {
        await initAuth();
    }, 100);

    // Initialize Lucide icons
    lucide.createIcons();
});

// Export functions for HTML access
window.handleFileUpload = handleFileUpload;
window.loadSampleData = loadSampleData;
window.updateMapping = updateMapping;
window.proceedToAnalysis = proceedToAnalysis;
window.goToStep = goToStep;
window.resetAnalysis = resetAnalysis;
window.showResultTab = showResultTab;
window.filterAlerts = filterAlerts;
window.toggleAlertDetails = toggleAlertDetails;
window.downloadResults = downloadResults;
window.toggleUserMenu = toggleUserMenu;
window.handleSignOut = handleSignOut;
window.showAnalysisHistory = showAnalysisHistory;
window.closeHistoryModal = closeHistoryModal;
window.showProfileSettings = showProfileSettings;
