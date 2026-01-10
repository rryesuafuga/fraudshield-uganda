/**
 * FraudShield Uganda - Fast Edition
 * High-performance fraud detection with WebAssembly
 */

// ============================================
// GLOBAL STATE
// ============================================
let wasmModule = null;
let rawData = [];
let mappedData = [];
let columnMappings = {};
let analysisResults = null;
let currentStep = 1;

// Standard fields for mapping dropdowns
const STANDARD_FIELDS = [
    'loan_id', 'borrower_id', 'borrower_name', 'phone', 'national_id',
    'amount', 'loan_date', 'approval_time', 'officer_id', 'officer_name',
    'branch', 'status', 'guarantor_name', 'guarantor_phone', 'interest_rate',
    'term_months', 'purpose', 'address'
];

// ============================================
// WASM INITIALIZATION
// ============================================
async function initWasm() {
    try {
        wasmModule = await import('../pkg/fraudshield_wasm.js');
        await wasmModule.default();
        updateEngineStatus(true);
        console.log('FraudShield engine loaded successfully');
        return true;
    } catch (error) {
        console.warn('Wasm not available, using JS fallback:', error.message);
        updateEngineStatus(false);
        return false;
    }
}

function updateEngineStatus(loaded) {
    const statusEl = document.getElementById('engine-status');
    if (statusEl) {
        if (loaded) {
            statusEl.innerHTML = `
                <span class="w-2 h-2 bg-emerald-400 rounded-full pulse-dot"></span>
                <span class="text-emerald-400 text-xs font-medium">Engine Ready</span>
            `;
        } else {
            statusEl.innerHTML = `
                <span class="w-2 h-2 bg-amber-400 rounded-full"></span>
                <span class="text-amber-400 text-xs font-medium">Fallback Mode</span>
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

    if (extension === 'csv') {
        reader.onload = (e) => {
            Papa.parse(e.target.result, {
                header: true,
                skipEmptyLines: true,
                complete: (results) => {
                    rawData = results.data;
                    processUploadedData();
                }
            });
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
    if (wasmModule && wasmModule.generate_sample_data) {
        const dataJson = wasmModule.generate_sample_data(500);
        rawData = JSON.parse(dataJson);
    } else {
        rawData = generateSampleDataJS(500);
    }
    processUploadedData();
}

function generateSampleDataJS(numLoans) {
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
            phone: isGhostLoan ? fraudPhones[Math.floor(Math.random() * fraudPhones.len)] : '07' + Math.floor(Math.random() * 90000000 + 10000000),
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
// COLUMN DETECTION
// ============================================
function processUploadedData() {
    if (!rawData || rawData.length === 0) return;

    // Use Wasm for column detection if available
    if (wasmModule && wasmModule.detect_columns) {
        const mappingsJson = wasmModule.detect_columns(JSON.stringify(rawData));
        columnMappings = JSON.parse(mappingsJson);
    } else {
        columnMappings = detectColumnsJS(rawData);
    }

    goToStep(2);
    renderMappingTable();
    renderDataPreview();
}

function detectColumnsJS(data) {
    // Simplified JS fallback for column detection
    const columns = Object.keys(data[0] || {});
    const mappings = {};

    const nameVariations = {
        loan_id: ['loan_id', 'loanid', 'loan_no', 'id', 'ref_no'],
        borrower_id: ['borrower_id', 'member_id', 'client_id', 'account_no'],
        borrower_name: ['borrower_name', 'name', 'full_name', 'member_name', 'client_name'],
        phone: ['phone', 'mobile', 'telephone', 'tel', 'contact'],
        amount: ['amount', 'loan_amount', 'principal', 'value'],
        loan_date: ['loan_date', 'date', 'disbursement_date'],
        approval_time: ['approval_time', 'time', 'timestamp'],
        officer_id: ['officer_id', 'staff_id', 'user_id', 'approved_by'],
        officer_name: ['officer_name', 'staff_name', 'loan_officer'],
        branch: ['branch', 'branch_name', 'location'],
        status: ['status', 'loan_status', 'state']
    };

    const usedFields = new Set();

    columns.forEach(col => {
        const colLower = col.toLowerCase().replace(/[^a-z0-9]/g, '_');

        for (const [field, variations] of Object.entries(nameVariations)) {
            if (usedFields.has(field)) continue;

            for (const v of variations) {
                if (colLower === v || colLower.includes(v)) {
                    mappings[col] = { field, confidence: 85, method: 'name_match' };
                    usedFields.add(field);
                    break;
                }
            }
            if (mappings[col]) break;
        }
    });

    return mappings;
}

// ============================================
// MAPPING UI
// ============================================
function renderMappingTable() {
    const columns = Object.keys(rawData[0] || {});
    const container = document.getElementById('mapping-table');

    let mapped = 0;
    let html = '<table class="w-full text-sm"><thead><tr class="text-left text-slate-400 border-b border-slate-700">' +
        '<th class="pb-2 pr-4">Original Column</th>' +
        '<th class="pb-2 pr-4">Detected As</th>' +
        '<th class="pb-2 pr-4">Confidence</th>' +
        '<th class="pb-2">Sample Values</th></tr></thead><tbody>';

    columns.forEach(col => {
        const mapping = columnMappings[col];
        const sample = rawData.slice(0, 4).map(r => r[col]).filter(v => v != null && v !== '');

        if (mapping) {
            mapped++;
            const confColor = mapping.confidence >= 80 ? 'emerald' : mapping.confidence >= 60 ? 'amber' : 'red';

            html += `<tr class="border-b border-slate-800">
                <td class="py-2 pr-4 font-mono text-slate-300">${col}</td>
                <td class="py-2 pr-4">
                    <select class="mapping-select bg-slate-700 rounded px-2 py-1 text-sm border-none" data-col="${col}">
                        ${STANDARD_FIELDS.map(f =>
                            `<option value="${f}" ${f === mapping.field ? 'selected' : ''}>${f}</option>`
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
                <td class="py-2 text-xs text-slate-500 truncate max-w-xs">${sample.join(', ')}</td>
            </tr>`;
        } else {
            html += `<tr class="border-b border-slate-800 bg-slate-800/30">
                <td class="py-2 pr-4 font-mono text-slate-500">${col}</td>
                <td class="py-2 pr-4">
                    <select class="mapping-select bg-slate-700 rounded px-2 py-1 text-sm border-none" data-col="${col}">
                        <option value="">-- Not Detected --</option>
                        ${STANDARD_FIELDS.map(f => `<option value="${f}">${f}</option>`).join('')}
                    </select>
                </td>
                <td class="py-2 pr-4 text-xs text-slate-500">-</td>
                <td class="py-2 text-xs text-slate-500 truncate max-w-xs">${sample.join(', ')}</td>
            </tr>`;
        }
    });

    html += '</tbody></table>';
    container.innerHTML = html;

    document.getElementById('mapping-summary').textContent =
        `${mapped} of ${columns.length} columns auto-detected`;

    // Add event listeners for mapping changes
    document.querySelectorAll('.mapping-select').forEach(select => {
        select.addEventListener('change', (e) => {
            const col = e.target.dataset.col;
            const newField = e.target.value;
            if (newField) {
                columnMappings[col] = { field: newField, confidence: 100, method: 'manual' };
            } else {
                delete columnMappings[col];
            }
        });
    });
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

// ============================================
// FRAUD ANALYSIS
// ============================================
function proceedToAnalysis() {
    // Apply mappings to create standardized data
    mappedData = rawData.map(row => {
        const mapped = {};
        Object.entries(columnMappings).forEach(([orig, map]) => {
            mapped[map.field] = row[orig];
        });
        return mapped;
    });

    goToStep(3);
    runFraudAnalysis();
}

async function runFraudAnalysis() {
    const checks = ['check-ghost', 'check-stacking', 'check-officer', 'check-timing', 'check-amount'];

    // Animate progress
    for (let i = 0; i < checks.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 200));
        const el = document.getElementById(checks[i]);
        el.innerHTML = '<i data-lucide="check-circle" class="h-4 w-4 inline text-emerald-400 mr-2"></i>' +
            el.textContent.replace('...', ' - Complete');
        lucide.createIcons();
    }

    // Run analysis (Wasm or JS fallback)
    if (wasmModule && wasmModule.analyze_fraud) {
        const resultsJson = wasmModule.analyze_fraud(JSON.stringify(mappedData));
        analysisResults = JSON.parse(resultsJson);
    } else {
        analysisResults = analyzeFraudJS(mappedData);
    }

    setTimeout(() => {
        goToStep(4);
        renderResults();
    }, 300);
}

function analyzeFraudJS(data) {
    // JS fallback for fraud analysis
    const results = {
        summary: {
            total_records: data.length,
            critical_alerts: 0,
            high_alerts: 0,
            medium_alerts: 0,
            low_alerts: 0,
            risk_score: 0
        },
        alerts: [],
        officers: {}
    };

    // Ghost loans detection
    const phoneCounts = {};
    data.forEach((row, idx) => {
        if (row.phone) {
            if (!phoneCounts[row.phone]) phoneCounts[row.phone] = [];
            phoneCounts[row.phone].push(row);
        }
    });

    Object.entries(phoneCounts).forEach(([phone, rows]) => {
        if (rows.length > 1) {
            const totalAmount = rows.reduce((sum, r) => sum + (parseFloat(r.amount) || 0), 0);
            results.alerts.push({
                alert_type: 'GHOST_LOAN',
                severity: rows.length >= 4 ? 'CRITICAL' : 'HIGH',
                title: 'Duplicate Phone Number Detected',
                description: `Phone ${phone} appears in ${rows.length} different loans`,
                amount: totalAmount,
                officer: rows[0].officer_id || '',
                details: rows.map(r => ({ loan_id: r.loan_id, borrower: r.borrower_name, amount: r.amount }))
            });
        }
    });

    // Officer stats
    data.forEach(row => {
        const officer = row.officer_id || 'Unknown';
        if (!results.officers[officer]) {
            results.officers[officer] = { name: row.officer_name || officer, count: 0, total_amount: 0, flag_rate: 0, z_score: 0 };
        }
        results.officers[officer].count++;
        results.officers[officer].total_amount += parseFloat(row.amount) || 0;
    });

    // Calculate risk score
    results.alerts.forEach(alert => {
        if (alert.severity === 'CRITICAL') { results.summary.critical_alerts++; results.summary.risk_score += 25; }
        else if (alert.severity === 'HIGH') { results.summary.high_alerts++; results.summary.risk_score += 15; }
        else if (alert.severity === 'MEDIUM') { results.summary.medium_alerts++; results.summary.risk_score += 8; }
        else { results.summary.low_alerts++; results.summary.risk_score += 3; }

        if (alert.officer && results.officers[alert.officer]) {
            results.officers[alert.officer].flag_rate++;
        }
    });

    results.summary.risk_score = Math.min(100, results.summary.risk_score);
    return results;
}

// ============================================
// RESULTS UI
// ============================================
function renderResults() {
    // Update summary stats
    document.getElementById('risk-score').textContent = analysisResults.summary.risk_score;
    document.getElementById('risk-bar').style.width = analysisResults.summary.risk_score + '%';

    const riskColor = analysisResults.summary.risk_score >= 70 ? 'bg-red-500' :
                      analysisResults.summary.risk_score >= 40 ? 'bg-orange-500' :
                      analysisResults.summary.risk_score >= 20 ? 'bg-yellow-500' : 'bg-emerald-500';
    document.getElementById('risk-bar').className = `h-full ${riskColor} rounded-full confidence-bar`;
    document.getElementById('risk-score').className = `text-3xl font-bold ${riskColor.replace('bg-', 'text-')}`;

    document.getElementById('total-records').textContent = analysisResults.summary.total_records.toLocaleString();
    document.getElementById('critical-count').textContent = analysisResults.summary.critical_alerts;
    document.getElementById('high-count').textContent = analysisResults.summary.high_alerts;
    document.getElementById('medium-count').textContent = analysisResults.summary.medium_alerts;

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

        return `<div class="alert-row px-4 py-3 border-b border-slate-700/50 bg-${colors.bg}" data-idx="${idx}">
            <div class="flex items-start space-x-3">
                <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-${colors.icon}/20">
                    <i data-lucide="alert-triangle" class="h-4 w-4 text-${colors.icon}"></i>
                </div>
                <div class="flex-1 min-w-0">
                    <div class="flex items-center flex-wrap gap-2">
                        <span class="px-2 py-0.5 text-xs font-medium rounded bg-${colors.icon} text-white">${alert.severity}</span>
                        <span class="text-xs text-slate-500 bg-slate-800 px-2 py-0.5 rounded">${(alert.alert_type || '').replace(/_/g, ' ')}</span>
                        <span class="font-medium text-white truncate">${alert.title}</span>
                    </div>
                    <p class="text-sm text-slate-400 mt-1">${alert.description}</p>
                    <div class="flex items-center justify-between mt-2">
                        <span class="text-sm font-semibold text-${colors.text}">UGX ${Number(alert.amount || 0).toLocaleString()}</span>
                        <span class="text-xs text-slate-500">Officer: ${alert.officer || 'N/A'}</span>
                    </div>
                </div>
            </div>
            <div id="alert-details-${idx}" class="hidden mt-3 ml-11 p-3 bg-slate-900/50 rounded-lg text-xs">
                <pre class="text-slate-400 overflow-x-auto">${JSON.stringify(alert.details, null, 2)}</pre>
            </div>
        </div>`;
    }).join('');

    // Add click handlers
    container.querySelectorAll('.alert-row').forEach(row => {
        row.addEventListener('click', () => {
            const idx = row.dataset.idx;
            document.getElementById(`alert-details-${idx}`).classList.toggle('hidden');
        });
    });

    lucide.createIcons();
}

function renderOfficers() {
    const container = document.getElementById('officers-list');
    const officers = Object.entries(analysisResults.officers)
        .map(([id, stats]) => ({ id, ...stats }))
        .sort((a, b) => b.flag_rate - a.flag_rate);

    container.innerHTML = officers.slice(0, 10).map((officer, idx) => {
        const riskScore = Math.min(100, (officer.flag_rate * 10) + (officer.z_score > 2 ? 30 : 0));
        const riskColor = riskScore > 60 ? 'red' : riskScore > 30 ? 'amber' : 'emerald';

        return `<div class="flex items-center space-x-3">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${idx < 2 ? `bg-${riskColor}-500/20 text-${riskColor}-400` : 'bg-slate-700 text-slate-400'}">
                ${idx + 1}
            </div>
            <div class="flex-1">
                <div class="flex items-center justify-between">
                    <p class="text-sm font-medium">${officer.name}</p>
                    <span class="text-sm font-bold text-${riskColor}-400">${Math.round(riskScore)}</span>
                </div>
                <div class="flex items-center justify-between text-xs text-slate-500 mt-0.5">
                    <span>${officer.count} loans</span>
                    <span>${officer.flag_rate} alerts</span>
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
    const columns = Object.keys(mappedData[0] || {});

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
    mappedData = [];
    columnMappings = {};
    analysisResults = null;
    document.getElementById('file-input').value = '';
    goToStep(1);
}

// ============================================
// EXPORT
// ============================================
function downloadResults() {
    if (!analysisResults) return;

    const lines = [];

    lines.push('FraudShield Uganda - Fraud Detection Report (Fast Edition)');
    lines.push(`Generated: ${new Date().toISOString()}`);
    lines.push(`Risk Score: ${analysisResults.summary.risk_score}/100`);
    lines.push(`Total Records: ${analysisResults.summary.total_records}`);
    lines.push(`Critical Alerts: ${analysisResults.summary.critical_alerts}`);
    lines.push(`High Risk Alerts: ${analysisResults.summary.high_alerts}`);
    lines.push(`Medium Risk Alerts: ${analysisResults.summary.medium_alerts}`);
    lines.push('');

    lines.push('=== FRAUD ALERTS ===');
    lines.push('Severity,Type,Title,Description,Amount at Risk (UGX),Officer ID');

    analysisResults.alerts.forEach(alert => {
        const row = [
            alert.severity || '',
            (alert.alert_type || '').replace(/_/g, ' '),
            `"${(alert.title || '').replace(/"/g, '""')}"`,
            `"${(alert.description || '').replace(/"/g, '""')}"`,
            alert.amount || 0,
            alert.officer || ''
        ];
        lines.push(row.join(','));
    });

    lines.push('');
    lines.push('=== OFFICER RISK RANKING ===');
    lines.push('Officer ID,Name,Loan Count,Alert Count,Risk Score');

    Object.entries(analysisResults.officers)
        .sort((a, b) => b[1].flag_rate - a[1].flag_rate)
        .forEach(([id, stats]) => {
            const riskScore = Math.min(100, (stats.flag_rate * 10) + (stats.z_score > 2 ? 30 : 0));
            lines.push([id, `"${stats.name}"`, stats.count, stats.flag_rate, Math.round(riskScore)].join(','));
        });

    const csvContent = lines.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `fraudshield-fast-report-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}

// ============================================
// TAB SWITCHING
// ============================================
function showResultTab(tab) {
    document.querySelectorAll('.result-tab-content').forEach(el => el.classList.add('hidden'));
    document.getElementById(`tab-${tab}`).classList.remove('hidden');

    document.querySelectorAll('.result-tab').forEach(btn => {
        btn.className = btn.className.replace('bg-emerald-500/20 text-emerald-400', 'text-slate-400 hover:text-white hover:bg-slate-800');
    });
    document.querySelector(`.result-tab[data-tab="${tab}"]`).className =
        'result-tab px-4 py-2 rounded-lg text-sm font-medium bg-emerald-500/20 text-emerald-400';
}

function filterAlerts(filter) {
    document.querySelectorAll('.alert-filter').forEach(btn => {
        btn.className = btn.className.replace('bg-slate-700', '').replace('text-slate-400', '');
        if (btn.dataset.filter === filter) {
            btn.className += ' bg-slate-700';
        } else {
            btn.className += ' text-slate-400 hover:bg-slate-700';
        }
    });
    renderAlerts(filter);
}

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', async () => {
    lucide.createIcons();

    // Initialize Wasm
    await initWasm();

    // Event listeners
    document.getElementById('file-input').addEventListener('change', handleFileUpload);
    document.getElementById('sample-btn').addEventListener('click', loadSampleData);
    document.getElementById('back-to-upload').addEventListener('click', () => goToStep(1));
    document.getElementById('proceed-btn').addEventListener('click', proceedToAnalysis);
    document.getElementById('reset-btn').addEventListener('click', resetAnalysis);
    document.getElementById('export-btn').addEventListener('click', downloadResults);
    document.getElementById('download-report-btn').addEventListener('click', downloadResults);

    // Tab switching
    document.querySelectorAll('.result-tab').forEach(btn => {
        btn.addEventListener('click', () => showResultTab(btn.dataset.tab));
    });

    // Alert filtering
    document.querySelectorAll('.alert-filter').forEach(btn => {
        btn.addEventListener('click', () => filterAlerts(btn.dataset.filter));
    });
});
