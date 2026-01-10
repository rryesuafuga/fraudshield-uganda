use wasm_bindgen::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

// Initialize panic hook for better error messages
#[wasm_bindgen(start)]
pub fn init() {
    #[cfg(feature = "console_error_panic_hook")]
    console_error_panic_hook::set_once();
}

// ============================================
// DATA STRUCTURES
// ============================================

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct ColumnMapping {
    pub field: String,
    pub confidence: u32,
    pub method: String,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct LoanRecord {
    pub loan_id: Option<String>,
    pub borrower_id: Option<String>,
    pub borrower_name: Option<String>,
    pub phone: Option<String>,
    pub national_id: Option<String>,
    pub amount: Option<f64>,
    pub loan_date: Option<String>,
    pub approval_time: Option<String>,
    pub officer_id: Option<String>,
    pub officer_name: Option<String>,
    pub branch: Option<String>,
    pub status: Option<String>,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct FraudAlert {
    pub alert_type: String,
    pub severity: String,
    pub title: String,
    pub description: String,
    pub amount: f64,
    pub officer: String,
    pub details: Vec<serde_json::Value>,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct OfficerStats {
    pub name: String,
    pub count: u32,
    pub total_amount: f64,
    pub flag_rate: u32,
    pub z_score: f64,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct AnalysisSummary {
    pub total_records: u32,
    pub critical_alerts: u32,
    pub high_alerts: u32,
    pub medium_alerts: u32,
    pub low_alerts: u32,
    pub risk_score: u32,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct AnalysisResults {
    pub summary: AnalysisSummary,
    pub alerts: Vec<FraudAlert>,
    pub officers: HashMap<String, OfficerStats>,
}

// ============================================
// NAME VARIATIONS FOR COLUMN MATCHING
// ============================================

fn get_name_variations() -> HashMap<&'static str, Vec<&'static str>> {
    let mut variations = HashMap::new();

    variations.insert("loan_id", vec![
        "loan_id", "loanid", "loan_no", "loan_number", "loan_ref", "reference",
        "loan_reference", "contract_id", "contract_no", "application_id",
        "disbursement_id", "txn_id", "transaction_id", "id", "ref_no"
    ]);

    variations.insert("borrower_id", vec![
        "borrower_id", "borrowerid", "member_id", "memberid", "client_id",
        "clientid", "customer_id", "customerid", "member_no", "member_number",
        "client_no", "account_no", "account_number", "sacco_no"
    ]);

    variations.insert("borrower_name", vec![
        "borrower_name", "borrowername", "name", "full_name", "fullname",
        "member_name", "membername", "client_name", "clientname",
        "customer_name", "customername", "applicant_name", "applicant"
    ]);

    variations.insert("phone", vec![
        "phone", "phone_number", "phonenumber", "mobile", "mobile_number",
        "mobilenumber", "telephone", "tel", "contact", "contact_number",
        "cell", "cellphone", "phone_no", "tel_no", "mobile_no"
    ]);

    variations.insert("national_id", vec![
        "national_id", "nationalid", "national_id_no", "nin", "id_no",
        "id_number", "idno", "national_identification", "id_card",
        "identification", "nid", "govt_id", "government_id"
    ]);

    variations.insert("amount", vec![
        "amount", "loan_amount", "loanamount", "principal", "principal_amount",
        "disbursed_amount", "disbursement", "approved_amount", "requested_amount",
        "credit_amount", "facility_amount", "sum", "total", "value"
    ]);

    variations.insert("loan_date", vec![
        "loan_date", "loandate", "disbursement_date", "date_disbursed",
        "issue_date", "created_date", "application_date", "approved_date",
        "date", "transaction_date", "txn_date", "start_date"
    ]);

    variations.insert("approval_time", vec![
        "approval_time", "time", "created_at", "timestamp", "datetime",
        "approved_time", "creation_time", "entry_time"
    ]);

    variations.insert("officer_id", vec![
        "officer_id", "officerid", "loan_officer_id", "staff_id", "staffid",
        "employee_id", "employeeid", "user_id", "userid", "approved_by",
        "created_by", "processed_by", "agent_id", "agent_code"
    ]);

    variations.insert("officer_name", vec![
        "officer_name", "officername", "loan_officer", "loanofficer",
        "staff_name", "staffname", "approved_by_name", "agent_name"
    ]);

    variations.insert("branch", vec![
        "branch", "branch_name", "branchname", "branch_id", "branchid",
        "branch_code", "location", "office", "center", "unit"
    ]);

    variations.insert("status", vec![
        "status", "loan_status", "loanstatus", "state", "current_status",
        "account_status", "disbursement_status"
    ]);

    variations
}

// ============================================
// COLUMN DETECTION
// ============================================

#[wasm_bindgen]
pub fn detect_columns(data_json: &str) -> String {
    let data: Vec<HashMap<String, serde_json::Value>> = match serde_json::from_str(data_json) {
        Ok(d) => d,
        Err(_) => return "{}".to_string(),
    };

    if data.is_empty() {
        return "{}".to_string();
    }

    let columns: Vec<String> = data[0].keys().cloned().collect();
    let variations = get_name_variations();
    let mut mappings: HashMap<String, ColumnMapping> = HashMap::new();
    let mut used_fields: std::collections::HashSet<String> = std::collections::HashSet::new();

    // Collect all potential mappings with scores
    let mut all_detections: Vec<(String, String, u32, String)> = Vec::new();

    for col in &columns {
        let col_lower = col.to_lowercase().replace(|c: char| !c.is_alphanumeric(), "_");
        let sample: Vec<String> = data.iter()
            .take(100)
            .filter_map(|row| row.get(col))
            .filter_map(|v| match v {
                serde_json::Value::String(s) => Some(s.clone()),
                serde_json::Value::Number(n) => Some(n.to_string()),
                _ => None,
            })
            .filter(|s| !s.is_empty())
            .collect();

        // Try name matching
        for (field, vars) in &variations {
            for var in vars {
                // Exact match
                if col_lower == *var {
                    all_detections.push((col.clone(), field.to_string(), 100, "exact_match".to_string()));
                }
                // Contains match
                else if col_lower.contains(var) || var.contains(&col_lower.as_str()) {
                    all_detections.push((col.clone(), field.to_string(), 85, "name_match".to_string()));
                }
                // Fuzzy match
                else {
                    let similarity = string_similarity(&col_lower, var);
                    if similarity > 0.7 {
                        let score = (similarity * 100.0) as u32;
                        all_detections.push((col.clone(), field.to_string(), score, "fuzzy_match".to_string()));
                    }
                }
            }
        }

        // Pattern detection
        if !sample.is_empty() {
            if let Some((field, confidence)) = detect_by_pattern(&sample) {
                all_detections.push((col.clone(), field, confidence, "pattern".to_string()));
            }
        }

        // Statistical detection
        if !sample.is_empty() {
            if let Some((field, confidence)) = detect_by_statistics(&sample) {
                all_detections.push((col.clone(), field, confidence, "statistics".to_string()));
            }
        }
    }

    // Sort by confidence descending
    all_detections.sort_by(|a, b| b.2.cmp(&a.2));

    // Assign best matches avoiding duplicates
    for (col, field, confidence, method) in all_detections {
        if !mappings.contains_key(&col) && !used_fields.contains(&field) && confidence > 40 {
            mappings.insert(col.clone(), ColumnMapping {
                field: field.clone(),
                confidence,
                method,
            });
            used_fields.insert(field);
        }
    }

    serde_json::to_string(&mappings).unwrap_or_else(|_| "{}".to_string())
}

fn string_similarity(s1: &str, s2: &str) -> f64 {
    if s1.is_empty() || s2.is_empty() {
        return 0.0;
    }

    let longer = if s1.len() > s2.len() { s1 } else { s2 };
    let shorter = if s1.len() > s2.len() { s2 } else { s1 };

    let longer_len = longer.len();
    if longer_len == 0 {
        return 1.0;
    }

    let edit_distance = levenshtein_distance(longer, shorter);
    (longer_len as f64 - edit_distance as f64) / longer_len as f64
}

fn levenshtein_distance(s1: &str, s2: &str) -> usize {
    let s1_chars: Vec<char> = s1.chars().collect();
    let s2_chars: Vec<char> = s2.chars().collect();
    let m = s1_chars.len();
    let n = s2_chars.len();

    let mut dp = vec![vec![0; n + 1]; m + 1];

    for i in 0..=m {
        dp[i][0] = i;
    }
    for j in 0..=n {
        dp[0][j] = j;
    }

    for i in 1..=m {
        for j in 1..=n {
            let cost = if s1_chars[i - 1] == s2_chars[j - 1] { 0 } else { 1 };
            dp[i][j] = (dp[i - 1][j] + 1)
                .min(dp[i][j - 1] + 1)
                .min(dp[i - 1][j - 1] + cost);
        }
    }

    dp[m][n]
}

fn detect_by_pattern(sample: &[String]) -> Option<(String, u32)> {
    // Phone detection
    let phone_matches: usize = sample.iter()
        .filter(|v| {
            let cleaned = v.replace(&[' ', '-', '(', ')'][..], "");
            cleaned.len() >= 10 && cleaned.len() <= 15 &&
            cleaned.chars().filter(|c| c.is_numeric()).count() >= 9
        })
        .count();

    if phone_matches as f64 / sample.len() as f64 > 0.7 {
        return Some(("phone".to_string(), 90));
    }

    // Date detection
    let date_matches: usize = sample.iter()
        .filter(|v| {
            v.contains('-') && v.len() >= 8 && v.len() <= 10 &&
            v.chars().filter(|c| c.is_numeric()).count() >= 6
        })
        .count();

    if date_matches as f64 / sample.len() as f64 > 0.7 {
        return Some(("loan_date".to_string(), 85));
    }

    // Time detection
    let time_matches: usize = sample.iter()
        .filter(|v| {
            v.contains(':') && v.len() >= 4 && v.len() <= 8 &&
            v.chars().filter(|c| c.is_numeric()).count() >= 3
        })
        .count();

    if time_matches as f64 / sample.len() as f64 > 0.7 {
        return Some(("approval_time".to_string(), 80));
    }

    None
}

fn detect_by_statistics(sample: &[String]) -> Option<(String, u32)> {
    // Check if numeric
    let numeric_values: Vec<f64> = sample.iter()
        .filter_map(|v| v.replace(',', "").parse::<f64>().ok())
        .collect();

    if numeric_values.len() as f64 / sample.len() as f64 > 0.9 {
        let mean = numeric_values.iter().sum::<f64>() / numeric_values.len() as f64;
        let min = numeric_values.iter().cloned().fold(f64::INFINITY, f64::min);
        let max = numeric_values.iter().cloned().fold(f64::NEG_INFINITY, f64::max);

        // Amount detection: large positive numbers
        if min >= 0.0 && mean > 100000.0 {
            return Some(("amount".to_string(), 75));
        }

        // Interest rate: 0-100 range
        if min >= 0.0 && max <= 100.0 && mean < 50.0 {
            return Some(("interest_rate".to_string(), 60));
        }
    }

    // Check for names (2+ words, alphabetic)
    let name_matches: usize = sample.iter()
        .filter(|v| {
            let words: Vec<&str> = v.split_whitespace().collect();
            words.len() >= 2 && words.iter().all(|w| w.chars().all(|c| c.is_alphabetic() || c == '-' || c == '\''))
        })
        .count();

    if name_matches as f64 / sample.len() as f64 > 0.7 {
        return Some(("borrower_name".to_string(), 70));
    }

    // Check for status keywords
    let status_keywords = ["active", "inactive", "paid", "closed", "pending", "approved",
        "rejected", "defaulted", "completed", "disbursed", "overdue"];
    let status_matches: usize = sample.iter()
        .filter(|v| status_keywords.iter().any(|kw| v.to_lowercase().contains(kw)))
        .count();

    if status_matches as f64 / sample.len() as f64 > 0.5 {
        return Some(("status".to_string(), 80));
    }

    None
}

// ============================================
// FRAUD DETECTION ALGORITHMS
// ============================================

#[wasm_bindgen]
pub fn analyze_fraud(data_json: &str) -> String {
    let data: Vec<LoanRecord> = match serde_json::from_str(data_json) {
        Ok(d) => d,
        Err(_) => return "{}".to_string(),
    };

    let mut results = AnalysisResults {
        summary: AnalysisSummary {
            total_records: data.len() as u32,
            critical_alerts: 0,
            high_alerts: 0,
            medium_alerts: 0,
            low_alerts: 0,
            risk_score: 0,
        },
        alerts: Vec::new(),
        officers: HashMap::new(),
    };

    // Run all detection algorithms
    detect_ghost_loans(&data, &mut results);
    detect_loan_stacking(&data, &mut results);
    detect_officer_anomalies(&data, &mut results);
    detect_timing_anomalies(&data, &mut results);
    detect_amount_anomalies(&data, &mut results);

    // Calculate risk score
    calculate_risk_score(&mut results);

    serde_json::to_string(&results).unwrap_or_else(|_| "{}".to_string())
}

fn detect_ghost_loans(data: &[LoanRecord], results: &mut AnalysisResults) {
    let mut phone_map: HashMap<String, Vec<&LoanRecord>> = HashMap::new();

    for record in data {
        if let Some(ref phone) = record.phone {
            if !phone.is_empty() {
                phone_map.entry(phone.clone()).or_default().push(record);
            }
        }
    }

    for (phone, records) in phone_map {
        if records.len() > 1 {
            let total_amount: f64 = records.iter()
                .filter_map(|r| r.amount)
                .sum();

            let severity = if records.len() >= 4 { "CRITICAL" } else { "HIGH" };

            let details: Vec<serde_json::Value> = records.iter()
                .map(|r| serde_json::json!({
                    "loan_id": r.loan_id,
                    "borrower": r.borrower_name,
                    "amount": r.amount
                }))
                .collect();

            results.alerts.push(FraudAlert {
                alert_type: "GHOST_LOAN".to_string(),
                severity: severity.to_string(),
                title: "Duplicate Phone Number Detected".to_string(),
                description: format!("Phone {} appears in {} different loans", phone, records.len()),
                amount: total_amount,
                officer: records.first().and_then(|r| r.officer_id.clone()).unwrap_or_default(),
                details,
            });
        }
    }
}

fn detect_loan_stacking(data: &[LoanRecord], results: &mut AnalysisResults) {
    let mut borrower_date_map: HashMap<String, Vec<&LoanRecord>> = HashMap::new();

    for record in data {
        if let (Some(ref borrower_id), Some(ref date)) = (&record.borrower_id, &record.loan_date) {
            let key = format!("{}-{}", borrower_id, date);
            borrower_date_map.entry(key).or_default().push(record);
        }
    }

    for (_, records) in borrower_date_map {
        if records.len() > 1 {
            let total_amount: f64 = records.iter()
                .filter_map(|r| r.amount)
                .sum();

            let details: Vec<serde_json::Value> = records.iter()
                .map(|r| serde_json::json!({
                    "loan_id": r.loan_id,
                    "amount": r.amount,
                    "date": r.loan_date
                }))
                .collect();

            results.alerts.push(FraudAlert {
                alert_type: "LOAN_STACKING".to_string(),
                severity: "HIGH".to_string(),
                title: "Multiple Loans Same Day".to_string(),
                description: format!("Borrower received {} loans on same date, total UGX {}",
                    records.len(), format_number(total_amount)),
                amount: total_amount,
                officer: records.first().and_then(|r| r.officer_id.clone()).unwrap_or_default(),
                details,
            });
        }
    }
}

fn detect_officer_anomalies(data: &[LoanRecord], results: &mut AnalysisResults) {
    let mut officer_stats: HashMap<String, OfficerStats> = HashMap::new();

    for record in data {
        let officer_id = record.officer_id.clone().unwrap_or_else(|| "Unknown".to_string());
        let stats = officer_stats.entry(officer_id.clone()).or_insert(OfficerStats {
            name: record.officer_name.clone().unwrap_or(officer_id),
            count: 0,
            total_amount: 0.0,
            flag_rate: 0,
            z_score: 0.0,
        });
        stats.count += 1;
        stats.total_amount += record.amount.unwrap_or(0.0);
    }

    // Calculate statistics
    let counts: Vec<f64> = officer_stats.values().map(|s| s.count as f64).collect();
    let mean = counts.iter().sum::<f64>() / counts.len() as f64;
    let variance = counts.iter().map(|c| (c - mean).powi(2)).sum::<f64>() / counts.len() as f64;
    let std_dev = variance.sqrt();

    for (officer_id, stats) in officer_stats.iter_mut() {
        let z_score = if std_dev > 0.0 { (stats.count as f64 - mean) / std_dev } else { 0.0 };
        stats.z_score = z_score;

        if z_score > 2.0 {
            let severity = if z_score > 3.0 { "HIGH" } else { "MEDIUM" };

            results.alerts.push(FraudAlert {
                alert_type: "OFFICER_ANOMALY".to_string(),
                severity: severity.to_string(),
                title: "Unusual Officer Volume".to_string(),
                description: format!("Officer {} processed {} loans ({:.1} std from avg)",
                    stats.name, stats.count, z_score),
                amount: stats.total_amount * 0.1,
                officer: officer_id.clone(),
                details: vec![serde_json::json!({
                    "officer_name": stats.name,
                    "loan_count": stats.count,
                    "z_score": z_score
                })],
            });
        }
    }

    results.officers = officer_stats;
}

fn detect_timing_anomalies(data: &[LoanRecord], results: &mut AnalysisResults) {
    for record in data {
        if let Some(ref time) = record.approval_time {
            if let Some(hour) = time.split(':').next().and_then(|h| h.parse::<u32>().ok()) {
                if hour < 6 || hour >= 22 {
                    results.alerts.push(FraudAlert {
                        alert_type: "TIMING_ANOMALY".to_string(),
                        severity: "MEDIUM".to_string(),
                        title: "After-Hours Approval".to_string(),
                        description: format!("Loan {} approved at {}",
                            record.loan_id.as_deref().unwrap_or("Unknown"), time),
                        amount: record.amount.unwrap_or(0.0),
                        officer: record.officer_id.clone().unwrap_or_default(),
                        details: vec![serde_json::json!({
                            "loan_id": record.loan_id,
                            "time": time,
                            "hour": hour
                        })],
                    });
                }
            }
        }
    }
}

fn detect_amount_anomalies(data: &[LoanRecord], results: &mut AnalysisResults) {
    let amounts: Vec<f64> = data.iter()
        .filter_map(|r| r.amount)
        .filter(|a| *a > 0.0)
        .collect();

    if amounts.len() < 5 {
        return;
    }

    let mean = amounts.iter().sum::<f64>() / amounts.len() as f64;
    let variance = amounts.iter().map(|a| (a - mean).powi(2)).sum::<f64>() / amounts.len() as f64;
    let std_dev = variance.sqrt();
    let threshold = mean + (2.5 * std_dev);

    for record in data {
        if let Some(amount) = record.amount {
            if amount > threshold {
                let pct_above = ((amount / mean - 1.0) * 100.0) as i32;

                results.alerts.push(FraudAlert {
                    alert_type: "AMOUNT_ANOMALY".to_string(),
                    severity: "MEDIUM".to_string(),
                    title: "Unusually Large Loan".to_string(),
                    description: format!("Loan amount UGX {} is {}% above average",
                        format_number(amount), pct_above),
                    amount,
                    officer: record.officer_id.clone().unwrap_or_default(),
                    details: vec![serde_json::json!({
                        "loan_id": record.loan_id,
                        "amount": amount,
                        "mean": mean,
                        "threshold": threshold
                    })],
                });
            }
        }
    }
}

fn calculate_risk_score(results: &mut AnalysisResults) {
    let mut score = 0u32;

    for alert in &results.alerts {
        match alert.severity.as_str() {
            "CRITICAL" => { score += 25; results.summary.critical_alerts += 1; }
            "HIGH" => { score += 15; results.summary.high_alerts += 1; }
            "MEDIUM" => { score += 8; results.summary.medium_alerts += 1; }
            _ => { score += 3; results.summary.low_alerts += 1; }
        }

        // Update officer flag rate
        if let Some(officer) = results.officers.get_mut(&alert.officer) {
            officer.flag_rate += 1;
        }
    }

    results.summary.risk_score = score.min(100);
}

// ============================================
// SAMPLE DATA GENERATION
// ============================================

#[wasm_bindgen]
pub fn generate_sample_data(num_loans: u32) -> String {
    let first_names = ["John", "Mary", "Peter", "Grace", "David", "Sarah", "James", "Agnes", "Robert", "Florence"];
    let last_names = ["Mukasa", "Nakato", "Ssemakula", "Nambi", "Okello", "Akello", "Wasswa", "Babirye", "Kato", "Nalongo"];
    let officers = ["OFF001", "OFF002", "OFF003", "OFF004", "OFF005"];
    let branches = ["Kampala Central", "Entebbe", "Jinja", "Mbarara", "Gulu"];
    let statuses = ["active", "active", "active", "completed", "defaulted"];

    let mut data: Vec<serde_json::Value> = Vec::new();
    let mut fraud_phones: Vec<String> = Vec::new();

    // Create fraud phone numbers
    for i in 0..5 {
        fraud_phones.push(format!("07{:08}", 10000000 + i * 1234567));
    }

    for i in 0..num_loans {
        let is_fraud = simple_random(i) < 5;  // ~5% fraud
        let is_ghost = is_fraud && simple_random(i + 1000) < 50;
        let is_stacking = is_fraud && !is_ghost && simple_random(i + 2000) < 50;

        let hour = if is_fraud && !is_ghost && !is_stacking {
            if simple_random(i + 3000) < 50 {
                simple_random(i + 4000) % 5  // 0-4 AM
            } else {
                22 + (simple_random(i + 5000) % 2)  // 22-23
            }
        } else {
            8 + (simple_random(i + 6000) % 10)  // 8-17
        };

        let phone = if is_ghost {
            fraud_phones[simple_random(i + 7000) as usize % fraud_phones.len()].clone()
        } else {
            format!("07{:08}", 10000000 + simple_random(i + 8000) * 12345)
        };

        let borrower_id = if is_stacking {
            format!("MBR{:04}", i / 3)
        } else {
            format!("MBR{:04}", i + 1)
        };

        let first = first_names[simple_random(i + 9000) as usize % first_names.len()];
        let last = last_names[simple_random(i + 10000) as usize % last_names.len()];

        data.push(serde_json::json!({
            "loan_id": format!("LN{:05}", i + 1),
            "borrower_id": borrower_id,
            "borrower_name": format!("{} {}", first, last),
            "phone": phone,
            "amount": 500000 + (simple_random(i + 11000) as u64 * 40000),
            "loan_date": format!("2024-{:02}-{:02}",
                1 + (simple_random(i + 12000) % 12),
                1 + (simple_random(i + 13000) % 28)),
            "approval_time": format!("{:02}:{:02}", hour, simple_random(i + 14000) % 60),
            "officer_id": if is_fraud { officers[0] } else { officers[simple_random(i + 15000) as usize % officers.len()] },
            "branch": branches[simple_random(i + 16000) as usize % branches.len()],
            "status": statuses[simple_random(i + 17000) as usize % statuses.len()]
        }));
    }

    serde_json::to_string(&data).unwrap_or_else(|_| "[]".to_string())
}

// Simple deterministic pseudo-random for consistent sample data
fn simple_random(seed: u32) -> u32 {
    let mut x = seed.wrapping_add(0x9E3779B9);
    x = x ^ (x >> 16);
    x = x.wrapping_mul(0x85EBCA6B);
    x = x ^ (x >> 13);
    x = x.wrapping_mul(0xC2B2AE35);
    x = x ^ (x >> 16);
    x % 100
}

fn format_number(n: f64) -> String {
    let n = n as i64;
    let s = n.to_string();
    let mut result = String::new();
    let chars: Vec<char> = s.chars().collect();

    for (i, c) in chars.iter().enumerate() {
        if i > 0 && (chars.len() - i) % 3 == 0 {
            result.push(',');
        }
        result.push(*c);
    }

    result
}
