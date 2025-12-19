import React, { useState, useCallback } from 'react';
import { AlertTriangle, Shield, Upload, FileSpreadsheet, Users, TrendingUp, AlertCircle, CheckCircle, XCircle, BarChart3, PieChart, Activity, Download, RefreshCw, ChevronRight, Eye, Filter } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RechartsPie, Pie, Cell, LineChart, Line, Legend } from 'recharts';

// ============================================
// FRAUDSHIELD UGANDA - DEMO DASHBOARD
// Demonstrates: CSV Upload → Analysis → Results
// ============================================

// Simulated fraud detection rules (in production, this would be Python backend)
const FraudDetectionEngine = {
  // Rule 1: Detect duplicate phone numbers (ghost loans indicator)
  detectDuplicatePhones: (data) => {
    const phoneCounts = {};
    const alerts = [];
    
    data.forEach((row, idx) => {
      const phone = row.phone || row.phone_number || row.borrower_phone;
      if (phone) {
        if (!phoneCounts[phone]) phoneCounts[phone] = [];
        phoneCounts[phone].push({ ...row, rowIndex: idx });
      }
    });
    
    Object.entries(phoneCounts).forEach(([phone, rows]) => {
      if (rows.length > 1) {
        alerts.push({
          type: 'GHOST_LOAN',
          severity: 'HIGH',
          title: 'Duplicate Phone Number Detected',
          description: `Phone ${phone} appears in ${rows.length} different loans`,
          affectedRows: rows.map(r => r.rowIndex),
          details: rows.map(r => ({
            loanId: r.loan_id || r.id,
            borrower: r.borrower_name || r.name,
            amount: r.amount || r.loan_amount
          }))
        });
      }
    });
    
    return alerts;
  },

  // Rule 2: Detect same-day multiple loans to same borrower
  detectLoanStacking: (data) => {
    const alerts = [];
    const borrowerDates = {};
    
    data.forEach((row, idx) => {
      const borrowerId = row.borrower_id || row.member_id || row.client_id;
      const date = row.loan_date || row.disbursement_date || row.date;
      
      if (borrowerId && date) {
        const key = `${borrowerId}-${date}`;
        if (!borrowerDates[key]) borrowerDates[key] = [];
        borrowerDates[key].push({ ...row, rowIndex: idx });
      }
    });
    
    Object.entries(borrowerDates).forEach(([key, rows]) => {
      if (rows.length > 1) {
        const [borrowerId, date] = key.split('-');
        const totalAmount = rows.reduce((sum, r) => sum + (parseFloat(r.amount || r.loan_amount || 0)), 0);
        
        alerts.push({
          type: 'LOAN_STACKING',
          severity: 'HIGH',
          title: 'Multiple Loans Same Day',
          description: `Borrower received ${rows.length} loans on ${date} totaling ${totalAmount.toLocaleString()}`,
          affectedRows: rows.map(r => r.rowIndex),
          details: rows
        });
      }
    });
    
    return alerts;
  },

  // Rule 3: Detect officer self-lending patterns
  detectSelfLending: (data) => {
    const alerts = [];
    
    data.forEach((row, idx) => {
      const officerId = row.officer_id || row.approved_by || row.loan_officer;
      const borrowerId = row.borrower_id || row.member_id || row.client_id;
      
      if (officerId && borrowerId && officerId === borrowerId) {
        alerts.push({
          type: 'SELF_LENDING',
          severity: 'CRITICAL',
          title: 'Officer Self-Lending Detected',
          description: `Officer ${officerId} approved loan for themselves`,
          affectedRows: [idx],
          details: [row]
        });
      }
    });
    
    return alerts;
  },

  // Rule 4: Detect unusual approval times (after hours)
  detectAfterHoursApprovals: (data) => {
    const alerts = [];
    
    data.forEach((row, idx) => {
      const time = row.approval_time || row.time || row.created_at;
      if (time) {
        const hour = parseInt(time.split(':')[0]) || new Date(time).getHours();
        if (hour < 7 || hour > 19) {
          alerts.push({
            type: 'AFTER_HOURS',
            severity: 'MEDIUM',
            title: 'After-Hours Approval',
            description: `Loan approved at unusual time: ${time}`,
            affectedRows: [idx],
            details: [row]
          });
        }
      }
    });
    
    return alerts;
  },

  // Rule 5: Detect unusual loan amounts (statistical outliers)
  detectAmountAnomalies: (data) => {
    const alerts = [];
    const amounts = data.map(r => parseFloat(r.amount || r.loan_amount || 0)).filter(a => a > 0);
    
    if (amounts.length > 5) {
      const mean = amounts.reduce((a, b) => a + b, 0) / amounts.length;
      const stdDev = Math.sqrt(amounts.reduce((sq, n) => sq + Math.pow(n - mean, 2), 0) / amounts.length);
      const threshold = mean + (2.5 * stdDev);
      
      data.forEach((row, idx) => {
        const amount = parseFloat(row.amount || row.loan_amount || 0);
        if (amount > threshold) {
          alerts.push({
            type: 'AMOUNT_ANOMALY',
            severity: 'MEDIUM',
            title: 'Unusually Large Loan Amount',
            description: `Amount ${amount.toLocaleString()} is ${((amount / mean) * 100 - 100).toFixed(0)}% above average`,
            affectedRows: [idx],
            details: [{ ...row, mean, stdDev, threshold }]
          });
        }
      });
    }
    
    return alerts;
  },

  // Rule 6: Officer concentration analysis
  detectOfficerConcentration: (data) => {
    const alerts = [];
    const officerCounts = {};
    
    data.forEach((row) => {
      const officer = row.officer_id || row.approved_by || row.loan_officer || 'Unknown';
      if (!officerCounts[officer]) officerCounts[officer] = { count: 0, totalAmount: 0 };
      officerCounts[officer].count++;
      officerCounts[officer].totalAmount += parseFloat(row.amount || row.loan_amount || 0);
    });
    
    const totalLoans = data.length;
    
    Object.entries(officerCounts).forEach(([officer, stats]) => {
      const percentage = (stats.count / totalLoans) * 100;
      if (percentage > 40 && stats.count > 10) {
        alerts.push({
          type: 'OFFICER_CONCENTRATION',
          severity: 'MEDIUM',
          title: 'High Officer Concentration',
          description: `Officer ${officer} processed ${percentage.toFixed(1)}% of all loans (${stats.count} loans worth ${stats.totalAmount.toLocaleString()})`,
          affectedRows: [],
          details: [{ officer, ...stats, percentage }]
        });
      }
    });
    
    return alerts;
  },

  // Main analysis function
  analyze: (data) => {
    const alerts = [
      ...FraudDetectionEngine.detectDuplicatePhones(data),
      ...FraudDetectionEngine.detectLoanStacking(data),
      ...FraudDetectionEngine.detectSelfLending(data),
      ...FraudDetectionEngine.detectAfterHoursApprovals(data),
      ...FraudDetectionEngine.detectAmountAnomalies(data),
      ...FraudDetectionEngine.detectOfficerConcentration(data)
    ];
    
    // Calculate risk scores
    const riskScore = Math.min(100, alerts.reduce((score, alert) => {
      if (alert.severity === 'CRITICAL') return score + 25;
      if (alert.severity === 'HIGH') return score + 15;
      if (alert.severity === 'MEDIUM') return score + 8;
      return score + 3;
    }, 0));
    
    return {
      alerts,
      riskScore,
      summary: {
        totalRecords: data.length,
        criticalAlerts: alerts.filter(a => a.severity === 'CRITICAL').length,
        highAlerts: alerts.filter(a => a.severity === 'HIGH').length,
        mediumAlerts: alerts.filter(a => a.severity === 'MEDIUM').length,
        lowAlerts: alerts.filter(a => a.severity === 'LOW').length
      }
    };
  }
};

// CSV Parser (simple implementation)
const parseCSV = (text) => {
  const lines = text.trim().split('\n');
  const headers = lines[0].split(',').map(h => h.trim().toLowerCase().replace(/['"]/g, '').replace(/\s+/g, '_'));
  
  return lines.slice(1).map(line => {
    const values = line.split(',').map(v => v.trim().replace(/['"]/g, ''));
    const row = {};
    headers.forEach((header, idx) => {
      row[header] = values[idx] || '';
    });
    return row;
  }).filter(row => Object.values(row).some(v => v !== ''));
};

// Sample data generator for demo
const generateSampleData = () => {
  const officers = ['OFF001', 'OFF002', 'OFF003', 'OFF004', 'OFF005'];
  const branches = ['Kampala Central', 'Entebbe', 'Jinja', 'Mbarara', 'Gulu'];
  const names = ['John Mukasa', 'Sarah Nambi', 'Peter Okello', 'Grace Auma', 'James Ssempala', 'Mary Nalwanga', 'David Kato', 'Rose Nabirye'];
  
  const data = [];
  
  // Generate normal loans
  for (let i = 0; i < 85; i++) {
    data.push({
      loan_id: `LN${String(i + 1).padStart(5, '0')}`,
      borrower_id: `MBR${String(Math.floor(Math.random() * 500) + 1).padStart(4, '0')}`,
      borrower_name: names[Math.floor(Math.random() * names.length)],
      phone: `+2567${Math.floor(Math.random() * 90000000 + 10000000)}`,
      amount: Math.floor(Math.random() * 4000000 + 500000),
      loan_date: `2024-${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}-${String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')}`,
      approval_time: `${String(Math.floor(Math.random() * 8) + 9).padStart(2, '0')}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}`,
      officer_id: officers[Math.floor(Math.random() * officers.length)],
      branch: branches[Math.floor(Math.random() * branches.length)],
      status: 'DISBURSED'
    });
  }
  
  // Inject fraudulent patterns for demo
  // Pattern 1: Duplicate phones (ghost loans)
  const ghostPhone = '+256701234567';
  for (let i = 0; i < 4; i++) {
    data.push({
      loan_id: `LN${String(86 + i).padStart(5, '0')}`,
      borrower_id: `MBR${String(600 + i).padStart(4, '0')}`,
      borrower_name: `Ghost Borrower ${i + 1}`,
      phone: ghostPhone,
      amount: Math.floor(Math.random() * 2000000 + 1000000),
      loan_date: '2024-11-15',
      approval_time: '14:30',
      officer_id: 'OFF002',
      branch: 'Kampala Central',
      status: 'DISBURSED'
    });
  }
  
  // Pattern 2: Loan stacking
  data.push({
    loan_id: 'LN00090',
    borrower_id: 'MBR0100',
    borrower_name: 'Stacker Client',
    phone: '+256709999999',
    amount: 3000000,
    loan_date: '2024-11-20',
    approval_time: '10:00',
    officer_id: 'OFF001',
    branch: 'Entebbe',
    status: 'DISBURSED'
  });
  data.push({
    loan_id: 'LN00091',
    borrower_id: 'MBR0100',
    borrower_name: 'Stacker Client',
    phone: '+256709999999',
    amount: 2500000,
    loan_date: '2024-11-20',
    approval_time: '15:30',
    officer_id: 'OFF003',
    branch: 'Jinja',
    status: 'DISBURSED'
  });
  
  // Pattern 3: Self-lending
  data.push({
    loan_id: 'LN00092',
    borrower_id: 'OFF004',
    borrower_name: 'Officer Self',
    phone: '+256708888888',
    amount: 5000000,
    loan_date: '2024-11-18',
    approval_time: '11:00',
    officer_id: 'OFF004',
    branch: 'Mbarara',
    status: 'DISBURSED'
  });
  
  // Pattern 4: After-hours approvals
  data.push({
    loan_id: 'LN00093',
    borrower_id: 'MBR0200',
    borrower_name: 'Late Night Loan',
    phone: '+256707777777',
    amount: 4500000,
    loan_date: '2024-11-19',
    approval_time: '23:45',
    officer_id: 'OFF002',
    branch: 'Kampala Central',
    status: 'DISBURSED'
  });
  
  // Pattern 5: Unusually large loan
  data.push({
    loan_id: 'LN00094',
    borrower_id: 'MBR0300',
    borrower_name: 'Big Loan Client',
    phone: '+256706666666',
    amount: 50000000,
    loan_date: '2024-11-21',
    approval_time: '09:15',
    officer_id: 'OFF001',
    branch: 'Kampala Central',
    status: 'DISBURSED'
  });
  
  return data;
};

// Main Dashboard Component
export default function FraudShieldDemo() {
  const [data, setData] = useState(null);
  const [results, setResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [filterSeverity, setFilterSeverity] = useState('ALL');

  const handleFileUpload = useCallback((event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target.result;
        const parsed = parseCSV(text);
        setData(parsed);
        runAnalysis(parsed);
      };
      reader.readAsText(file);
    }
  }, []);

  const loadSampleData = useCallback(() => {
    const sampleData = generateSampleData();
    setData(sampleData);
    runAnalysis(sampleData);
  }, []);

  const runAnalysis = (dataToAnalyze) => {
    setIsAnalyzing(true);
    // Simulate processing time for effect
    setTimeout(() => {
      const analysisResults = FraudDetectionEngine.analyze(dataToAnalyze);
      setResults(analysisResults);
      setIsAnalyzing(false);
    }, 1500);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return { bg: 'bg-red-500', text: 'text-red-500', light: 'bg-red-500/10', border: 'border-red-500' };
      case 'HIGH': return { bg: 'bg-orange-500', text: 'text-orange-500', light: 'bg-orange-500/10', border: 'border-orange-500' };
      case 'MEDIUM': return { bg: 'bg-yellow-500', text: 'text-yellow-500', light: 'bg-yellow-500/10', border: 'border-yellow-500' };
      default: return { bg: 'bg-blue-500', text: 'text-blue-500', light: 'bg-blue-500/10', border: 'border-blue-500' };
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'GHOST_LOAN': return <Users className="w-5 h-5" />;
      case 'LOAN_STACKING': return <BarChart3 className="w-5 h-5" />;
      case 'SELF_LENDING': return <AlertCircle className="w-5 h-5" />;
      case 'AFTER_HOURS': return <Activity className="w-5 h-5" />;
      case 'AMOUNT_ANOMALY': return <TrendingUp className="w-5 h-5" />;
      case 'OFFICER_CONCENTRATION': return <PieChart className="w-5 h-5" />;
      default: return <AlertTriangle className="w-5 h-5" />;
    }
  };

  const filteredAlerts = results?.alerts.filter(a => 
    filterSeverity === 'ALL' || a.severity === filterSeverity
  ) || [];

  // Chart data
  const severityChartData = results ? [
    { name: 'Critical', value: results.summary.criticalAlerts, fill: '#ef4444' },
    { name: 'High', value: results.summary.highAlerts, fill: '#f97316' },
    { name: 'Medium', value: results.summary.mediumAlerts, fill: '#eab308' },
    { name: 'Low', value: results.summary.lowAlerts, fill: '#3b82f6' }
  ].filter(d => d.value > 0) : [];

  const alertTypeData = results ? 
    Object.entries(results.alerts.reduce((acc, alert) => {
      acc[alert.type] = (acc[alert.type] || 0) + 1;
      return acc;
    }, {})).map(([type, count]) => ({ type: type.replace(/_/g, ' '), count })) : [];

  return (
    <div className="min-h-screen bg-slate-950 text-white" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      {/* Header */}
      <header className="bg-gradient-to-r from-emerald-900/50 to-slate-900 border-b border-emerald-800/30">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">FraudShield Uganda</h1>
                <p className="text-xs text-emerald-400">AI-Powered Fraud Detection Demo</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="px-3 py-1 bg-amber-500/20 text-amber-400 text-xs font-medium rounded-full">
                DEMO VERSION
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Upload Section - Show when no data */}
        {!data && (
          <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <div className="w-full max-w-2xl">
              <div className="text-center mb-8">
                <div className="w-20 h-20 bg-emerald-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <Shield className="w-10 h-10 text-emerald-400" />
                </div>
                <h2 className="text-3xl font-bold mb-3">Fraud Detection Analysis</h2>
                <p className="text-slate-400 text-lg">Upload your loan data to detect suspicious patterns</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                {/* File Upload */}
                <label className="group cursor-pointer">
                  <div className="border-2 border-dashed border-slate-700 rounded-2xl p-8 text-center hover:border-emerald-500 hover:bg-emerald-500/5 transition-all duration-300">
                    <div className="w-14 h-14 bg-slate-800 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:bg-emerald-500/20 transition-colors">
                      <Upload className="w-7 h-7 text-slate-400 group-hover:text-emerald-400" />
                    </div>
                    <h3 className="font-semibold mb-2">Upload CSV File</h3>
                    <p className="text-sm text-slate-500">Drag & drop or click to browse</p>
                    <p className="text-xs text-slate-600 mt-2">Supports: .csv, .xlsx</p>
                  </div>
                  <input 
                    type="file" 
                    accept=".csv,.xlsx" 
                    onChange={handleFileUpload}
                    className="hidden" 
                  />
                </label>

                {/* Sample Data Button */}
                <button 
                  onClick={loadSampleData}
                  className="border-2 border-dashed border-slate-700 rounded-2xl p-8 text-center hover:border-amber-500 hover:bg-amber-500/5 transition-all duration-300 group"
                >
                  <div className="w-14 h-14 bg-slate-800 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:bg-amber-500/20 transition-colors">
                    <FileSpreadsheet className="w-7 h-7 text-slate-400 group-hover:text-amber-400" />
                  </div>
                  <h3 className="font-semibold mb-2">Load Sample Data</h3>
                  <p className="text-sm text-slate-500">Try with pre-loaded demo data</p>
                  <p className="text-xs text-slate-600 mt-2">95 loans with fraud patterns</p>
                </button>
              </div>

              {/* Expected Format */}
              <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-800">
                <h4 className="font-semibold text-sm text-slate-300 mb-3">Expected CSV Format</h4>
                <div className="overflow-x-auto">
                  <code className="text-xs text-emerald-400 block whitespace-nowrap">
                    loan_id, borrower_id, borrower_name, phone, amount, loan_date, approval_time, officer_id, branch, status
                  </code>
                </div>
                <p className="text-xs text-slate-500 mt-3">
                  Column names are flexible - the system recognizes common variations
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isAnalyzing && (
          <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <div className="w-16 h-16 border-4 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin mb-6"></div>
            <h3 className="text-xl font-semibold mb-2">Analyzing Data...</h3>
            <p className="text-slate-400">Running fraud detection algorithms</p>
          </div>
        )}

        {/* Results Dashboard */}
        {results && !isAnalyzing && (
          <div className="space-y-6">
            {/* Top Stats */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {/* Risk Score */}
              <div className="col-span-2 md:col-span-1 bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl p-6 border border-slate-700">
                <div className="text-xs text-slate-400 uppercase tracking-wider mb-2">Risk Score</div>
                <div className={`text-4xl font-bold ${
                  results.riskScore >= 70 ? 'text-red-500' : 
                  results.riskScore >= 40 ? 'text-orange-500' : 
                  results.riskScore >= 20 ? 'text-yellow-500' : 'text-emerald-500'
                }`}>
                  {results.riskScore}
                </div>
                <div className="mt-2 h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all duration-500 ${
                      results.riskScore >= 70 ? 'bg-red-500' : 
                      results.riskScore >= 40 ? 'bg-orange-500' : 
                      results.riskScore >= 20 ? 'bg-yellow-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${results.riskScore}%` }}
                  />
                </div>
              </div>

              {/* Stats Cards */}
              <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-800">
                <div className="text-xs text-slate-400 mb-1">Records Analyzed</div>
                <div className="text-2xl font-bold text-white">{results.summary.totalRecords}</div>
              </div>
              
              <div className="bg-red-500/10 rounded-xl p-4 border border-red-500/20">
                <div className="text-xs text-red-400 mb-1">Critical Alerts</div>
                <div className="text-2xl font-bold text-red-500">{results.summary.criticalAlerts}</div>
              </div>
              
              <div className="bg-orange-500/10 rounded-xl p-4 border border-orange-500/20">
                <div className="text-xs text-orange-400 mb-1">High Alerts</div>
                <div className="text-2xl font-bold text-orange-500">{results.summary.highAlerts}</div>
              </div>
              
              <div className="bg-yellow-500/10 rounded-xl p-4 border border-yellow-500/20">
                <div className="text-xs text-yellow-400 mb-1">Medium Alerts</div>
                <div className="text-2xl font-bold text-yellow-500">{results.summary.mediumAlerts}</div>
              </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 border-b border-slate-800 pb-2">
              {['overview', 'alerts', 'data'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === tab 
                      ? 'bg-emerald-500/20 text-emerald-400' 
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Severity Distribution */}
                <div className="bg-slate-900/50 rounded-2xl p-6 border border-slate-800">
                  <h3 className="font-semibold mb-4">Alert Severity Distribution</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <RechartsPie>
                        <Pie
                          data={severityChartData}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={90}
                          paddingAngle={2}
                          dataKey="value"
                          label={({ name, value }) => `${name}: ${value}`}
                        >
                          {severityChartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </RechartsPie>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Alert Types */}
                <div className="bg-slate-900/50 rounded-2xl p-6 border border-slate-800">
                  <h3 className="font-semibold mb-4">Alerts by Type</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={alertTypeData} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                        <XAxis type="number" stroke="#94a3b8" />
                        <YAxis type="category" dataKey="type" stroke="#94a3b8" width={120} tick={{ fontSize: 11 }} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                        />
                        <Bar dataKey="count" fill="#10b981" radius={[0, 4, 4, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Top Alerts Preview */}
                <div className="lg:col-span-2 bg-slate-900/50 rounded-2xl p-6 border border-slate-800">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold">Critical & High Priority Alerts</h3>
                    <button 
                      onClick={() => setActiveTab('alerts')}
                      className="text-sm text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
                    >
                      View All <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="space-y-3">
                    {results.alerts
                      .filter(a => a.severity === 'CRITICAL' || a.severity === 'HIGH')
                      .slice(0, 5)
                      .map((alert, idx) => {
                        const colors = getSeverityColor(alert.severity);
                        return (
                          <div 
                            key={idx}
                            className={`flex items-center gap-4 p-4 rounded-xl ${colors.light} border ${colors.border}/30 cursor-pointer hover:bg-opacity-20 transition-colors`}
                            onClick={() => { setSelectedAlert(alert); setActiveTab('alerts'); }}
                          >
                            <div className={`w-10 h-10 rounded-lg ${colors.bg}/20 flex items-center justify-center ${colors.text}`}>
                              {getTypeIcon(alert.type)}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className={`text-xs font-medium px-2 py-0.5 rounded ${colors.bg} text-white`}>
                                  {alert.severity}
                                </span>
                                <span className="font-medium text-white truncate">{alert.title}</span>
                              </div>
                              <p className="text-sm text-slate-400 truncate mt-1">{alert.description}</p>
                            </div>
                            <Eye className="w-5 h-5 text-slate-500" />
                          </div>
                        );
                      })}
                  </div>
                </div>
              </div>
            )}

            {/* Alerts Tab */}
            {activeTab === 'alerts' && (
              <div className="space-y-4">
                {/* Filters */}
                <div className="flex items-center gap-3">
                  <Filter className="w-4 h-4 text-slate-400" />
                  <span className="text-sm text-slate-400">Filter:</span>
                  {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map((severity) => (
                    <button
                      key={severity}
                      onClick={() => setFilterSeverity(severity)}
                      className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                        filterSeverity === severity
                          ? severity === 'ALL' ? 'bg-slate-600 text-white' : `${getSeverityColor(severity).bg} text-white`
                          : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                      }`}
                    >
                      {severity}
                    </button>
                  ))}
                </div>

                {/* Alert List */}
                <div className="space-y-3">
                  {filteredAlerts.map((alert, idx) => {
                    const colors = getSeverityColor(alert.severity);
                    const isExpanded = selectedAlert === alert;
                    
                    return (
                      <div 
                        key={idx}
                        className={`rounded-xl border ${colors.border}/30 overflow-hidden transition-all duration-200 ${
                          isExpanded ? colors.light : 'bg-slate-900/50'
                        }`}
                      >
                        <div 
                          className="flex items-center gap-4 p-4 cursor-pointer hover:bg-slate-800/50 transition-colors"
                          onClick={() => setSelectedAlert(isExpanded ? null : alert)}
                        >
                          <div className={`w-10 h-10 rounded-lg ${colors.bg}/20 flex items-center justify-center ${colors.text}`}>
                            {getTypeIcon(alert.type)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className={`text-xs font-medium px-2 py-0.5 rounded ${colors.bg} text-white`}>
                                {alert.severity}
                              </span>
                              <span className="text-xs text-slate-500 bg-slate-800 px-2 py-0.5 rounded">
                                {alert.type.replace(/_/g, ' ')}
                              </span>
                              <span className="font-medium text-white">{alert.title}</span>
                            </div>
                            <p className="text-sm text-slate-400 mt-1">{alert.description}</p>
                          </div>
                          <ChevronRight className={`w-5 h-5 text-slate-500 transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
                        </div>
                        
                        {isExpanded && alert.details && (
                          <div className="px-4 pb-4 border-t border-slate-700/50">
                            <div className="mt-4 p-4 bg-slate-900/50 rounded-lg">
                              <h4 className="text-xs uppercase text-slate-500 mb-3">Affected Records</h4>
                              <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                  <thead>
                                    <tr className="text-left text-slate-400">
                                      {Object.keys(alert.details[0] || {}).slice(0, 5).map(key => (
                                        <th key={key} className="pb-2 pr-4 font-medium">{key}</th>
                                      ))}
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {alert.details.slice(0, 5).map((detail, dIdx) => (
                                      <tr key={dIdx} className="border-t border-slate-800">
                                        {Object.values(detail).slice(0, 5).map((val, vIdx) => (
                                          <td key={vIdx} className="py-2 pr-4 text-slate-300">
                                            {typeof val === 'number' ? val.toLocaleString() : String(val)}
                                          </td>
                                        ))}
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>

                {filteredAlerts.length === 0 && (
                  <div className="text-center py-12 text-slate-500">
                    <CheckCircle className="w-12 h-12 mx-auto mb-3 text-emerald-500/50" />
                    <p>No alerts found with selected filter</p>
                  </div>
                )}
              </div>
            )}

            {/* Data Tab */}
            {activeTab === 'data' && (
              <div className="bg-slate-900/50 rounded-2xl p-6 border border-slate-800">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold">Uploaded Data ({data.length} records)</h3>
                  <button className="text-sm text-emerald-400 hover:text-emerald-300 flex items-center gap-2">
                    <Download className="w-4 h-4" /> Export Report
                  </button>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-slate-400 border-b border-slate-700">
                        {Object.keys(data[0] || {}).map(key => (
                          <th key={key} className="pb-3 pr-4 font-medium whitespace-nowrap">{key}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {data.slice(0, 20).map((row, idx) => (
                        <tr key={idx} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                          {Object.values(row).map((val, vIdx) => (
                            <td key={vIdx} className="py-3 pr-4 text-slate-300 whitespace-nowrap">
                              {typeof val === 'number' ? val.toLocaleString() : String(val)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {data.length > 20 && (
                  <p className="text-center text-sm text-slate-500 mt-4">
                    Showing 20 of {data.length} records
                  </p>
                )}
              </div>
            )}

            {/* Action Bar */}
            <div className="flex items-center justify-between p-4 bg-slate-900/50 rounded-xl border border-slate-800">
              <button 
                onClick={() => { setData(null); setResults(null); }}
                className="px-4 py-2 text-slate-400 hover:text-white flex items-center gap-2"
              >
                <RefreshCw className="w-4 h-4" /> Analyze New Data
              </button>
              <div className="flex gap-3">
                <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm font-medium flex items-center gap-2">
                  <Download className="w-4 h-4" /> Download Report
                </button>
                <button className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-sm font-medium">
                  Contact FraudShield →
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 mt-12">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-slate-500">
            <p>© 2025 FraudShield Uganda | Demo Version - For Demonstration Purposes Only</p>
            <div className="flex items-center gap-4">
              <span>sseguya256@gmail.com</span>
              <span>+256 784 902 753</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
