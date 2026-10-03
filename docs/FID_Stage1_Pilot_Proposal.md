# Pilot Proposal — Fund for Innovation in Development (FID)

**Stage requested:** Stage 1 / Pilot grant (up to €200,000)

**Project title:** FedFraudShield Pilot — Testing privacy-preserving, collaborative fraud detection in 48 Ugandan SACCOs and microfinance institutions

**Country:** Uganda (ODA-eligible, OECD DAC list)

**Applicant:** FraudShield Uganda *(legal entity name and registration number to be inserted)*

**Lead:** Raymond R. Wayesu, Founder & Lead Data Scientist — raymondrwayesu@gmail.com · +256 784 902 753

**Research partner:** *(to be confirmed — see Section 10)*

**Duration:** 18 months

**Requested amount:** €198,500

**Date:** September 2026

> **Status of this document:** working draft prepared alongside the Stage 0 concept note (`docs/FID_Stage0_Concept_Note.md`). It assumes Stage 0 has been completed; every figure that Stage 0 is meant to produce is marked `[Stage 0 result]` and must be replaced with actual results. Items marked `[TBC]` must be confirmed before submission. FID rules (stage definitions, ceilings, eligible costs) must be re-checked against the current call guide on fundinnovation.dev.

---

## 1. Executive summary

Internal fraud drains an estimated 2–5% of portfolio value from Uganda's 28,500+ SACCOs and 150+ microfinance institutions every year — UGX 100–250 billion — and when a SACCO fails, its members, mostly rural and low-income households, lose their savings outright. No affordable, data-driven fraud detection exists for this sector: individual institutions have too little data to train a model, and Uganda's Data Protection and Privacy Act (DPPA 2019) prevents pooling raw records.

**FedFraudShield** solves both constraints at once. Each institution runs a rule-based detector (the FraudShield tool) on its own loan book and, optionally, a small local neural model whose *parameter updates only* — never raw data — are combined into a shared model across institutions. In simulation, federated training raised detection quality (AUPRC) from 0.64 to 0.95. Stage 0 `[Stage 0 result: summarise real-data validation with N partner SACCOs — precision/recall on confirmed cases, bandwidth, schema-mapping success rate]`.

This Stage 1 pilot will deploy the intervention in **48 institutions across four regions for 12 months**, randomising the timing of roll-out so that the pilot generates a credible first estimate of impact on fraud losses and portfolio quality while every participant receives the tool by the end of the pilot. It will answer the questions FID needs answered before a Stage 2 impact evaluation: Does it work on real data at scale? Do SACCO staff act on alerts? What does it cost per institution and per shilling of loss averted? And does federation add value over the rule-based tool alone?

---

## 2. Problem and target population

### 2.1 Who is affected and how

| Aspect | Detail |
|---|---|
| **Population** | ~18 million SACCO/MFI members in Uganda; predominantly rural, informal-sector households. `[TBC: cite share of women members; UCSCU/UMRA data]` |
| **Direct harm** | Loss of savings on SACCO collapse; higher interest and tighter lending to cover losses; exclusion from formal credit when a local SACCO fails. |
| **Sector loss** | UGX 100–250 billion / year (≈ USD 27–68 million), on a >UGX 5 trillion asset base. |
| **Institutional failure** | PROFIRA (2021): of 453 monitored SACCOs, 312 struggling due to fraud and governance failures; 64 collapsed. |
| **Why existing controls fail** | Manual audits sample 5–10% of loans; external audits detect ~3% of fraud (ACFE 2024). Bank-grade fraud tools are priced and designed for institutions with millions of transactions. |

### 2.2 Fraud typologies the intervention targets

| Typology | Mechanism | Detection signal |
|---|---|---|
| Ghost loans | Loans booked to fictitious borrowers; officer pockets disbursement | Shared phone numbers / IDs across "different" borrowers; missing repayment behaviour |
| Officer self-lending | Officer approves loans to self or proxies | Officer ID = borrower ID; approvals concentrated in one officer |
| Loan stacking | Same member takes multiple concurrent loans, often across branches | Same borrower, multiple disbursements same day / overlapping terms |
| Collusion rings | Officer + group of borrowers + shared guarantor | Shared guarantors, geographic clustering, timing patterns |
| Timing manipulation | Back-dated or after-hours entries to conceal activity | Approvals outside business hours; end-of-month bunching |
| Amount manipulation | Inflated disbursements, round-number loans | Statistical outliers vs. product and branch norms |

---

## 3. The innovation

### 3.1 Components

| Component | Function | Status |
|---|---|---|
| **FraudShield tool** (Layer 1, rule-based) | Ingests any CSV/Excel export; auto-maps columns via schema matching; runs deterministic and statistical rules for the typologies above; produces ranked alerts with evidence. Works from day one with no training data. | Prototyped; deployed in this repository (`mvp/`, `mvp-fast/`, `backend/`). `[Stage 0 result: validated on real data at N institutions]` |
| **FedFraudShield** (Layer 2, federated ML) | Each institution trains a lightweight model locally; differentially-private parameter updates (~100 KB per round) are aggregated on a server hosted in Uganda; the improved global model is returned. No raw data leaves any institution. | Architecture and simulation published (DSA 2026). `[Stage 0 result: federated proof-of-concept over real connectivity]` |
| **Alert and investigation workflow** | Weekly ranked alert list (capped to investigation capacity), SMS/WhatsApp notification, case-tracking sheet, feedback loop that labels confirmed/false cases for model improvement. | Designed; to be finalised in pilot month 1–2. |

### 3.2 What makes it new

- First federated-learning approach to SACCO/MFI fraud in Africa; gives institutions with **no fraud history** a working detector from day one.
- Built for the operating environment: heterogeneous software (Ensibuuko, Kanzu, Excel), 3G connectivity, DPPA 2019 compliance (§14 data minimality, §7(2)(b)(iii) fraud-prevention basis, §19 no cross-border transfer).
- A **deterrence channel** as well as a detection channel: staff who know transactions are monitored change behaviour before any case is proven.

### 3.3 Evidence to date

| Source | Finding |
|---|---|
| Simulation (PaySim, 15 institutions, non-IID) | Federated AUPRC 0.945 vs. 0.643 local-only (+47%); recall 0.99; 5 zero-history institutions gained detection capability; DP at ε = 5 retains AUPRC 0.69. |
| Stage 0 real-data validation | `[Stage 0 result: N institutions, M months of records; % of institution-confirmed fraud cases flagged; false-positive rate at chosen threshold; schema-mapping success on X software systems]` |
| Stage 0 federated PoC | `[Stage 0 result: rounds completed, bandwidth, model performance vs local-only on real data]` |
| Stage 0 baselines | `[Stage 0 result: median fraud-loss rate, PAR30/90, audit detection rate, cost of investigation per case]` |

---

## 4. Pilot objectives and learning questions

**Primary objective:** determine whether FedFraudShield reduces fraud losses and improves portfolio quality in real SACCOs at a cost that makes sector-wide adoption viable.

| # | Learning question | Answered by |
|---|---|---|
| Q1 | Does the tool detect real fraud that institutions' existing controls miss, and at what precision? | Alert-level validation; comparison with audit findings |
| Q2 | Do institutions act on alerts? What share are investigated, confirmed, and resolved? | Case-tracking data; process evaluation |
| Q3 | What is the effect on fraud losses, PAR30/PAR90 and write-offs after 12 months? | Phased-roll-out comparison (§6) |
| Q4 | Does federation (Layer 2) add measurable value over the rule-based tool alone (Layer 1)? | Two-arm treatment contrast |
| Q5 | What does it cost per institution, per confirmed case, and per UGX of loss averted? | Cost tracking; cost-effectiveness analysis |
| Q6 | Is there a deterrence effect visible in staff behaviour (after-hours entries, concentration) even before cases are proven? | Behavioural indicators from transaction data |
| Q7 | Are women members and women-led institutions differentially protected? | Gender-disaggregated outcomes |
| Q8 | What is needed for UMRA/UCSCU to operate the federation hub as sector infrastructure? | Governance workstream; stakeholder interviews |

---

## 5. Pilot sites and sample

| Parameter | Design |
|---|---|
| Number of institutions | **48** (40 SACCOs, 8 MFIs) `[TBC after Stage 0 power calculation]` |
| Regions | Central (Kampala/Mukono/Wakiso), Eastern (Jinja/Mbale), Western (Mbarara), Northern (Gulu) — 12 per region |
| Size range | 300–5,000 members; 12+ months of digital records; mix of Ensibuuko, Kanzu Banking, and Excel/QuickBooks users |
| Inclusion criteria | UMRA-licensed or UCSCU-affiliated; board consent; a named fraud focal person; exportable loan data |
| Exclusion criteria | Institutions under active regulatory sanction or receivership; institutions that participated in Stage 0 (they continue separately as demonstration sites) |
| Recruitment | Through UCSCU regional structures and UMRA `[TBC: letters of support]`; over-recruit 60 to allow for attrition |

---

## 6. Pilot design (phased roll-out with randomised timing)

A Stage 1 pilot must test the innovation in real conditions; FID also expects a credible learning design that prepares a Stage 2 impact evaluation. We use a **cluster-randomised phased roll-out** at institution level:

| Arm | n | Months 1–3 | Months 4–12 | Months 13–15 |
|---|---|---|---|---|
| **A — Early, full** | 16 | Onboarding | FraudShield tool + federation | Continues |
| **B — Early, rule-based only** | 16 | Onboarding | FraudShield tool only (no federation) | Federation added |
| **C — Delayed** | 16 | Baseline only | Baseline data collection only | Onboarding + full intervention |

- **Randomisation:** stratified by region and institution size, conducted by the research partner after baseline data collection; pre-registered (AEA RCT Registry or OSF) `[TBC]`.
- **Comparison 1 (A + B vs. C, months 4–12):** effect of the intervention on fraud losses and portfolio quality.
- **Comparison 2 (A vs. B):** value added by federation.
- **Fairness:** every institution receives the full intervention by month 15; C-arm institutions receive it free for the remainder of the grant.
- **Power:** with 32 treated vs. 16 control clusters, the pilot is powered to detect large effects on institution-level fraud-loss and PAR outcomes `[Stage 0 result: MDE from baseline variance]`. It is *not* powered for member-level outcomes — that is the purpose of Stage 2.

---

## 7. Implementation plan

| Phase | Months | Activities |
|---|---|---|
| **0. Set-up** | 1–2 | Finalise research partnership and pre-analysis plan; recruit and randomise 48 institutions; sign DPPA-compliant data-processing agreements; ethics approval `[TBC: UNCST / institutional REC]`; finalise alert workflow and case-tracking tools; procure local-node hardware. |
| **1. Baseline** | 2–3 | Extract 12–24 months of historical data at all 48 sites; run retrospective detection (results withheld from C-arm until month 13); establish baseline fraud-loss, PAR, audit-detection and investigation-cost measures; staff survey. |
| **2. Onboarding (A, B)** | 3–4 | Install local nodes; validate schema mapping per site; train fraud focal persons and boards (½-day workshop per region); go live with weekly alert cycle. |
| **3. Operation** | 4–12 | Weekly alert cycle at 32 sites; monthly federated training rounds at A-sites; monthly investigation-outcome collection; quarterly threshold tuning; help desk (WhatsApp) and regional field visits every 6 weeks. |
| **4. Roll-out to C; federation to B** | 13–15 | Onboard C-arm; enable federation at B-arm; all 48 sites on full intervention. |
| **5. Analysis and Stage 2 design** | 13–18 | Endline data extraction; impact, process and cost-effectiveness analysis; gender analysis; governance report with UMRA/UCSCU; Stage 2 proposal and full-scale evaluation design. |

**Alert workflow (per institution, weekly):** tool runs on latest export → top-N alerts (N set by investigation capacity, typically 5–10) sent to focal person → focal person records outcome (confirmed fraud / error / false positive / pending) in the case tracker → outcomes feed model recalibration and the evaluation dataset.

---

## 8. Evaluation design

### 8.1 Outcomes

| Level | Outcome | Source | Timing |
|---|---|---|---|
| Institution (primary) | Fraud losses as % of portfolio; number and value of confirmed fraud cases | Case tracker; audited accounts | Baseline, month 12, month 15 |
| Institution (primary) | PAR30, PAR90, write-offs | Loan book exports | Monthly |
| Institution (secondary) | Time from fraud event to detection; investigation cost per case; share of alerts investigated | Case tracker | Continuous |
| Behavioural (mechanism) | After-hours approvals, officer concentration, round-amount share | Transaction data | Monthly |
| Institution (secondary) | Solvency indicators; continued licensing; board-reported confidence | UMRA data; board survey | Baseline, endline |
| Member (exploratory) | Savings retained; loan access; interest rate; trust in institution | Member sample survey (n≈20 per institution) | Baseline, endline |
| Gender | All above disaggregated by member gender and women-led institutions | As above | As above |

### 8.2 Methods

- **Impact:** intention-to-treat comparison of A+B vs. C over months 4–12 with baseline controls; A vs. B for the federation contrast; difference-in-differences using monthly PAR series as a robustness check.
- **Process:** structured interviews with focal persons and boards at months 6 and 12; alert-log analysis (precision by typology, investigation rates, reasons for non-action).
- **Cost-effectiveness:** full costing of the intervention (development amortised, hardware, connectivity, hosting, training, support, institution staff time) against measured loss reduction and detection gains; comparison with the cost of manual audit per loan covered.
- **Detection accuracy:** precision/recall of alerts against confirmed cases, by typology and institution type; threshold sensitivity.

### 8.3 Ethics, consent and data protection

- Institutional consent from boards; staff informed that monitoring is in place (this is standard practice and part of the deterrence mechanism); member survey consent individually.
- Raw member data never leaves the institution; the research team receives only aggregate and de-identified alert/outcome data under a data-processing agreement; the aggregation server is hosted in Uganda.
- Alerts are triage inputs for the institution's own investigation, not accusations; disciplinary decisions remain entirely with the institution. A protocol will define how alerts are communicated to avoid unfair treatment of staff.
- Ethics review: `[TBC: Uganda National Council for Science and Technology and a registered research ethics committee]`.

---

## 9. Cost-effectiveness plan

| Item | Working figure | To be replaced by |
|---|---|---|
| Fraud loss per institution | 2–5% of portfolio; median SACCO in sample ≈ UGX 500 million portfolio → UGX 10–25 million/yr | Stage 0 baselines; pilot baseline |
| Intervention cost per institution per year (pilot, fully loaded) | ≈ €1,900 (≈ UGX 8 million) including onboarding; ≈ €700 recurring | Actual pilot costs |
| Break-even | Preventing 30–40% of median losses covers the recurring cost several times over | Measured loss reduction |
| Comparator | Manual internal audit: 5–10% loan coverage; external audit ≈ UGX 3–8 million/yr for a small SACCO with ~3% fraud detection | `[TBC: audit-cost survey]` |
| Metrics to report | Cost per institution-year; cost per confirmed case; cost per UGX 1 million of loss averted; cost per member protected | Endline analysis |

---

## 10. Team, partners and governance

| Role | Who | Responsibilities | Status |
|---|---|---|---|
| Principal Investigator / project lead | Raymond R. Wayesu (MSc Statistics, Linköping; Founder and Developer, Wayesu Community Research Organisation Ltd; author of FedFraudShield paper) | Overall delivery, detection engine, federation hub | Confirmed |
| Legal applicant | FraudShield Uganda `[TBC: entity, registration, bank account, audited accounts if required]` | Grant holder | **Must confirm — FID does not fund individuals** |
| Research partner (co-PI for evaluation) | `[TBC]` — candidates: Makerere University Dept. of Computer Science; a J-PAL-affiliated economist; IPA Uganda | Randomisation, pre-registration, evaluation analysis, publication | To be secured in Stage 0 |
| Field team | 1 field coordinator (Kampala) + 4 regional field officers (0.5 FTE each) | Recruitment, onboarding, training, case-tracker collection | To recruit |
| Engineering | 1 ML/backend engineer (1.0 FTE), 1 support engineer (0.5 FTE) | Local nodes, schema mapping, hub operations, help desk | To recruit |
| Sector partners | Uganda Cooperative Savings and Credit Union (UCSCU); Uganda Microfinance Regulatory Authority (UMRA) | Recruitment channels; governance workstream; pathway to sector-run hub | `[TBC: letters of support]` |
| Advisory group | Representatives of UMRA, UCSCU, 2 pilot SACCO boards, research partner, a data-protection lawyer | Quarterly review; ethics and fairness oversight | To convene month 1 |

**Governance:** monthly project management meeting; quarterly advisory group; quarterly narrative and financial report to FID; independent evaluation analysis owned by the research partner with publication rights.

---

## 11. Budget (18 months) — indicative, EUR

| Line | Amount | Basis |
|---|---|---|
| **Personnel** | | |
| Project lead (0.6 FTE × 18 mo) | 27,000 | Local rate |
| ML/backend engineer (1.0 FTE × 18 mo) | 27,000 | |
| Support engineer (0.5 FTE × 15 mo) | 9,000 | |
| Field coordinator (1.0 FTE × 18 mo) | 16,200 | |
| Regional field officers (4 × 0.5 FTE × 15 mo) | 24,000 | |
| *Personnel subtotal* | *103,200* | |
| **Research and evaluation** | | |
| Research partner sub-grant (design, randomisation, analysis, publication) | 28,000 | |
| Baseline and endline member surveys (48 × 20 × 2 rounds, enumerators, tablets) | 9,600 | |
| Ethics review fees, pre-registration, data-protection counsel | 3,500 | |
| *Research subtotal* | *41,100* | |
| **Deployment** | | |
| Local-node hardware (48 × mini-PC/laptop) | 14,400 | €300 each |
| Connectivity stipends (48 × 15 mo × €4) | 2,900 | |
| Aggregation server hosting in Uganda, security audit, backups | 6,000 | |
| SMS/WhatsApp alert gateway | 1,500 | |
| *Deployment subtotal* | *24,800* | |
| **Training and field operations** | | |
| Regional onboarding workshops (4 × 2 rounds) | 6,400 | Venue, transport, materials |
| Field travel (6-weekly site visits, 4 regions) | 9,000 | |
| Advisory group meetings and final dissemination workshop | 3,000 | |
| *Training/field subtotal* | *18,400* | |
| **Indirect / contingency** | | |
| Audit, accounting, insurance | 4,000 | |
| Contingency (≈3.5%) | 7,000 | |
| **Total requested** | **198,500** | |

Co-financing: founder's in-kind time and the existing FraudShield codebase (not costed); institutions contribute staff time for investigation and data exports. `[TBC: any other co-funding]`

---

## 12. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Recruitment shortfall / attrition | Medium | High | Over-recruit to 60; UCSCU/UMRA channels; no-cost participation; C-arm guaranteed the tool by month 13 |
| Institutions do not act on alerts | Medium | High | Cap alerts to capacity; focal-person training; board-level reporting; measure and report non-action as a finding (Q2) |
| High false-positive rate erodes trust | Medium | Medium | Stage 0 threshold calibration; quarterly re-tuning; typology-specific thresholds; precision tracked per site |
| Data quality / export failures at Excel-based sites | High | Medium | Schema-mapping module; field-officer support; minimum-data checklist at recruitment |
| Connectivity failures for federation rounds | Medium | Low | Asynchronous rounds; ~100 KB payloads; rounds can lag a month without harm |
| Staff intimidation or unfair action on the basis of alerts | Low | High | Alert communication protocol; alerts framed as triage, not accusation; advisory-group oversight; institution retains all decisions |
| Contamination (C-arm institutions change behaviour after hearing of the pilot) | Medium | Medium | Regional stratification; measure awareness at endline; interpret as lower bound |
| Regulatory objection to shared hub | Low | High | UMRA engaged from Stage 0; hub in Uganda; CRB regulations precedent; DPPA analysis in paper |
| Key-person dependency | Medium | High | Two engineers; documented codebase (open in this repository); research partner co-owns evaluation |

---

## 13. Timeline (18 months)

```
Month:               1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18
Set-up & recruitment ██████
Baseline & randomise    ██████
Onboarding A+B             ██████
Operation A+B (alerts)        ███████████████████████████
Federation rounds (A)         ███████████████████████████
Roll-out C, federation B                                 █████████
Process evaluation                  ██                ██
Endline data & surveys                                   ██████
Analysis & CE study                                         ███████████
Governance workstream            ████████████████████████████████████
Stage 2 design & proposal                                      ████████
Reporting to FID              ▲        ▲        ▲        ▲        ▲   ▲
```

---

## 14. Pathway to scale and Stage 2

| Step | What | When |
|---|---|---|
| Stage 2 impact evaluation (≤ €1.5M) | 150–300 institutions, full RCT powered on member-level outcomes, run by the research partner | Months 19–42 |
| Sector-run hub | Hand-over plan for UMRA or UCSCU to host the aggregation server and model registry; MoU drafted in this pilot | Month 18 deliverable |
| Open standards | Tazama (Linux Foundation) integration so detection logic is portable | During Stage 2 |
| Revenue model | Tiered subscription: free/low-cost for small SACCOs, cross-subsidised by MFIs and banks; pricing tested with pilot institutions at month 12 | Month 12–18 |
| Regional replication | Kenya, Tanzania, Rwanda SACCO sectors | Post-Stage 2 |

---

## 15. Alignment with FID selection criteria

| FID criterion | How this proposal meets it |
|---|---|
| **Impact on people living in poverty** | Protects savings and credit access of ~18M mostly rural, low-income members; prevents institutional collapse; gender-disaggregated measurement built in. |
| **Cost-effectiveness** | Full costing against measured loss reduction; comparison with manual audit; explicit break-even analysis. |
| **Potential for scale and sustainability** | Federation hub designed as sector infrastructure (UMRA/UCSCU); open-source integration; subscription model tested in pilot; regional replicability. |
| **Innovation** | First federated-learning fraud detection for SACCOs/MFIs in Africa; solves data scarcity and privacy law together. |
| **Readiness for Stage 1** | Prototyped and validated in Stage 0 `[Stage 0 result]`; ready for real-world testing at scale. |
| **Rigorous learning design** | Cluster-randomised phased roll-out, pre-registered, independent research partner; produces the estimates and power calculations needed for a Stage 2 RCT. |
| **Priority sectors** | Gender-equality dimension via women's reliance on SACCOs `[Stage 0 result: gender analysis]`; financial resilience of poor households. |

---

## 16. Annexes to prepare

- [ ] Stage 0 final report (real-data validation, baselines, federated PoC)
- [ ] Letters of intent from ≥ 48 candidate institutions (target 60)
- [ ] Letters of support from UMRA and UCSCU
- [ ] Research partner agreement and CVs of evaluation co-PI
- [ ] Pre-analysis plan draft
- [ ] Ethics approval or submission receipt
- [ ] Data-processing agreement template (DPPA 2019 compliant)
- [ ] Alert communication and staff-fairness protocol
- [ ] Detailed budget in FID template
- [ ] Legal registration documents and financial statements of the applicant
- [ ] `docs/FedFraudShield_DSA2026_Paper_v3.pdf` and link to this repository
