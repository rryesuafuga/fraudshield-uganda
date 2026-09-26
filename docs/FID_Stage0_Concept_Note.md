# Concept Note — Fund for Innovation in Development (FID)

**Stage requested:** Stage 0 / Preparation grant (up to €50,000)
**Project title:** FedFraudShield — Privacy-preserving, collaborative fraud detection to protect the savings of Uganda's SACCO and microfinance members
**Country:** Uganda (ODA-eligible, OECD DAC list)
**Applicant:** FraudShield Uganda *(legal entity name and registration number to be inserted)*
**Lead:** Raymond R. Wayesu, Founder & Lead Data Scientist — raymondrwayesu@gmail.com · +256 784 902 753
**Proposed research partner:** *(to be confirmed — see Section 8)*
**Duration:** 9 months
**Date:** September 2026

> **Status of this document:** working draft. Items marked `[TBC]` must be confirmed or replaced before submission. All FID rules (stage definitions, ceilings, eligibility) must be re-checked against the current call guide on fundinnovation.dev, which is updated periodically.

---

## 1. Summary

Uganda's 28,500+ Savings and Credit Cooperative Organisations (SACCOs) and 150+ licensed microfinance institutions (MFIs) hold the savings of roughly 18 million people, most of them rural and low-income. Internal fraud — ghost loans, officer self-lending, collusion rings — erodes an estimated 2–5% of portfolio value each year (UGX 100–250 billion). When a SACCO collapses, its members lose their savings outright; the 2021 PROFIRA assessment found 312 of 453 monitored SACCOs struggling due to fraud and governance failures, and 64 collapsed entirely.

Machine-learning fraud detection is standard in banks but absent from this sector, because no single SACCO has enough data to train a model and Uganda's Data Protection and Privacy Act (DPPA 2019) restricts pooling raw records. **FedFraudShield** is a federated-learning framework that lets many institutions train one shared fraud model without any raw data leaving their premises. In simulation (DSA 2026 workshop paper, in `docs/`), federated training raised detection quality (AUPRC) from 0.64 to 0.95 — a 47% relative improvement — and gave institutions with *no* fraud history a working detector. A companion tool, the **FraudShield MVP**, already runs rule-based and statistical checks on any SACCO's exported spreadsheet and is ready for field use.

This Stage 0 grant will convert a validated design into a pilot-ready intervention: secure data-sharing agreements with 3–5 SACCOs, validate the system on real Ugandan data, establish baseline fraud-loss measurements, recruit a research partner, and design the counterfactual evaluation for a Stage 1 pilot.

---

## 2. The problem, framed as a poverty and inequality problem

| Dimension | Evidence |
|---|---|
| Who is affected | ~18 million SACCO/MFI members; predominantly rural, informal-sector households. Women make up the majority of members in many SACCOs and village savings groups `[TBC: cite UCSCU/UMRA figure]`. |
| How they are harmed | Fraud losses are absorbed by members as (a) lost savings when a SACCO fails, (b) higher interest rates and stricter lending to cover losses, (c) loss of trust that pushes households back to informal, higher-cost credit. |
| Scale of loss | UGX 100–250 billion / year (≈ USD 27–68 million), 2–5% of a >UGX 5 trillion asset base. |
| Why existing responses fail | Manual audits sample 5–10% of loans; external audits detect ~3% of fraud (ACFE 2024). Commercial banking fraud tools are priced for banks and require data volumes SACCOs do not have. |
| Why now | SACCOs are digitising rapidly (Ensibuuko, Kanzu, Excel), creating the transaction records a detector needs; UMRA's licensing regime and the 2022 Credit Reference Bureau Regulations create both the regulatory pull and a precedent for cross-institution data cooperation. |

The intervention is therefore best understood as **protecting the financial assets of the poor** and **keeping community financial institutions solvent**, not as a technology sale to institutions.

---

## 3. The innovation

### 3.1 Two components, one intervention

| Component | What it is | Maturity |
|---|---|---|
| **FraudShield MVP** | Browser/Python tool that ingests any SACCO's CSV/Excel export, auto-maps its columns (schema matching), and runs rule-based + statistical detection: duplicate-phone ghost loans, same-day loan stacking, officer self-lending, after-hours approvals, amount outliers, officer concentration. | Working prototype; deployed at `mvp/` and `mvp-fast/` in this repository. Ready for real-world testing (FID Stage 1 criterion). |
| **FedFraudShield** | Hub-and-spoke federated learning: each SACCO trains a small neural model locally; only differentially-private parameter updates (~100 KB per round) go to an aggregation server hosted in Uganda; the improved global model is returned. No raw data leaves any institution. | Architecture and simulation results published (DSA 2026 workshop, work-in-progress). Not yet run on real Ugandan data. |

### 3.2 What is new

- First application of federated learning to SACCO/MFI fraud detection in Africa (no prior work found in the literature review in the paper).
- Solves the two blockers that have kept ML out of this sector simultaneously: **data scarcity** (pooling learning across institutions) and **privacy law** (DPPA 2019 §14 data minimality; §7(2)(b)(iii) fraud-prevention basis; §19 no cross-border transfer).
- Designed for the actual operating environment: works over 3G (30 MB total for 20 training rounds across 15 institutions), tolerates heterogeneous software and column names, and gives *zero-history* institutions a usable model from day one.

### 3.3 Evidence to date (simulation, PaySim dataset, 15 simulated institutions, non-IID)

| Method | AUPRC | Recall |
|---|---|---|
| Local-only (average institution) | 0.643 | 0.768 |
| Local-only (worst institution) | 0.005 | 0.033 |
| **FedAvg (federated)** | **0.945** | **0.991** |
| FedProx + differential privacy (ε = 5) | 0.692 | 0.312 |
| Centralised (oracle upper bound) | 0.977 | 0.995 |

Five simulated institutions had no fraud labels at all and could not train any detector alone; all five obtained a working detector through federation.

**Known limitations (stated honestly):** results are on synthetic mobile-money data, not real SACCO loan books; precision is low at default thresholds (many false positives — acceptable for an investigation-triage tool but must be tuned); strong privacy settings (ε = 1) degrade performance significantly. Stage 0 exists to address the first two.

---

## 4. Stage 0 objectives and activities

**Objective:** Reach the point where a Stage 1 pilot with a credible counterfactual design can begin.

| # | Activity | Output | Months |
|---|---|---|---|
| A1 | Institutional partnerships: sign data-sharing and pilot MoUs with 3–5 SACCOs/MFIs of varied size and software (Ensibuuko, Kanzu, Excel). Engage UMRA and UCSCU as observers. | Signed MoUs; DPPA-compliant data-processing agreements reviewed by counsel. | 1–3 |
| A2 | Real-data validation: run the FraudShield MVP on 12–24 months of historical records from each partner; validate the schema-mapping module across heterogeneous exports; retrospectively check flagged cases against each SACCO's own audit findings. | Precision/recall on real data; list of fraud typologies present in Ugandan loan data that PaySim lacks (ghost loans, collusion rings). | 2–6 |
| A3 | Baseline measurement: establish, per partner, current fraud-loss rate, portfolio-at-risk (PAR30/90), write-offs, audit detection rate, and cost of fraud investigation. | Baseline dataset and measurement protocol — the outcome variables for Stage 1/2. | 2–6 |
| A4 | Federated proof-of-concept on real data: deploy local training nodes at partners, run federated rounds over their actual connectivity, tune thresholds and privacy budget. | Technical feasibility report: bandwidth, latency, model performance vs. local-only on real data. | 4–8 |
| A5 | Research partnership and evaluation design: formalise an academic partner; pre-register a Stage 1 pilot design (see §5); power calculation from A3 baselines. | Evaluation pre-analysis plan; Stage 1 application. | 3–9 |
| A6 | Cost model: unit cost per institution per year for both components; comparison with cost of manual audit and average loss averted. | Cost-effectiveness note (§6). | 6–9 |
| A7 | Gender-disaggregated analysis: characterise whether women members and women-led SACCOs are differentially exposed to fraud losses. | Short analytic note feeding Stage 1 outcome selection. | 5–9 |

**Stage 0 deliverable:** a Stage 1 proposal with real-data evidence, signed partners, a pre-registered evaluation design, and a costed budget.

---

## 5. Evaluation pathway (what Stage 1 and Stage 2 would test)

FID requires impact evaluation with a counterfactual. The proposed design, to be finalised with the research partner in Stage 0:

- **Unit of randomisation:** SACCO/MFI (the tool operates at institution level).
- **Stage 1 pilot (≤ €200k, ~40–60 institutions):** institutions randomised to (T1) FraudShield MVP alone, (T2) FraudShield + FedFraudShield federation, or (C) waitlist control receiving the tool after 12 months. A phased roll-out design ensures every participant eventually receives the intervention.
- **Primary outcomes:** fraud losses as % of portfolio; PAR30/PAR90; number and value of confirmed fraud cases detected; institution solvency/continuation.
- **Member-level outcomes (Stage 2):** savings retained, access to credit, interest rates charged, member trust and continued participation; disaggregated by gender and rural/urban.
- **Secondary / mechanism outcomes:** time-to-detection, audit cost, staff behaviour (e.g. reduction in after-hours approvals — a deterrence effect that may appear even before a case is proven).
- **Stage 2 (≤ €1.5M):** scale to 150–300 institutions across regions, with a full randomised evaluation powered on member-level outcomes, run by the research partner.

Power will be calculated from Stage 0 baselines (A3). A cluster-randomised design at institution level with ~40–60 clusters is expected to be adequate for institution-level fraud-loss outcomes given the high baseline variance reported by PROFIRA; member-level outcomes will require Stage 2 scale.

---

## 6. Cost-effectiveness logic (to be quantified in Stage 0)

| Item | Working estimate | Source / status |
|---|---|---|
| Annual fraud loss, median SACCO | 2–5% of portfolio | Sector estimates; to be replaced by A3 baseline |
| Cost of FraudShield MVP per institution/year | UGX 6 million (≈ USD 1,600) at current pricing; marginal cost far lower at scale | Current price list |
| Marginal cost of federation node | Commodity laptop/VM + ~30 MB/month data | Paper §4.3 |
| Break-even | A SACCO with a UGX 500 million portfolio losing 3% (UGX 15 million/yr) breaks even if the tool prevents ~40% of that loss | Illustrative |
| Comparator | Manual audit covering 5–10% of loans; external audit detecting ~3% of fraud | ACFE 2024 |

Stage 0 will produce actual cost per institution, cost per fraud case detected, and cost per UGX of loss averted, benchmarked against manual audit.

---

## 7. Pathway to scale and sustainability

1. **Sector infrastructure, not a product:** the federated aggregation hub is designed to be operated as shared infrastructure by a sector body (UMRA as regulator, or UCSCU as the apex cooperative union), analogous to how the Credit Reference Bureau operates. This is the target for FID's *Public Policy Transformation* stage.
2. **Open standards:** integration with Tazama (Linux Foundation open-source fraud monitoring for emerging markets) so that the model layer is portable and not locked to one vendor.
3. **Revenue model for the tool layer:** subscription pricing already validated with early conversations; a tiered/free tier for the smallest SACCOs cross-subsidised by MFIs and banks.
4. **Regional replication:** Kenya, Tanzania and Rwanda have comparable SACCO sectors and data-protection regimes; the federated design transfers directly.

---

## 8. Team and partners

| Role | Who | Status |
|---|---|---|
| Lead / PI | Raymond R. Wayesu — MSc Statistics (Linköping University); Data Analytics Lead, Uganda Virus Research Institute; 10+ years in statistical analysis and ML; author of the FedFraudShield paper | Confirmed |
| Legal applicant | FraudShield Uganda `[TBC: registered entity type, registration no., bank account]` | **Must be confirmed — FID does not fund individuals** |
| Research partner (evaluation design & Stage 2 evaluation) | Candidates: Makerere University Dept. of Computer Science (Azamuke, Katarahweire, Bainomugisha — cited in the paper); a J-PAL-affiliated economist; Innovations for Poverty Action (IPA) Uganda | `[TBC]` — to be secured under A5 |
| Implementing partners | 3–5 SACCOs/MFIs `[TBC: names]` | Under discussion |
| Sector / regulatory observers | Uganda Microfinance Regulatory Authority (UMRA); Uganda Cooperative Savings and Credit Union (UCSCU); Ministry of Trade, Industry and Cooperatives | `[TBC]` |
| Legal counsel (DPPA compliance) | `[TBC]` | Budgeted |

---

## 9. Budget (Stage 0, 9 months) — indicative, EUR

| Line | Amount | Notes |
|---|---|---|
| Personnel: lead data scientist (0.6 FTE), one ML engineer (1.0 FTE), one field/partnerships coordinator (0.5 FTE) | 24,000 | Local salaries |
| Research partner engagement: evaluation design, power calculations, pre-registration | 8,000 | Sub-grant or consultancy |
| Partner SACCO costs: data extraction time, on-site node hardware (5 × laptop/VM), connectivity | 6,000 | |
| Legal: DPPA compliance review, data-processing agreements, MoU templates | 3,000 | |
| Aggregation server hosting in Uganda + security review | 2,500 | |
| Travel and field work (Kampala, Jinja, Mbarara, Gulu, Mbale) | 3,000 | |
| Stakeholder workshop (UMRA, UCSCU, partners) and dissemination | 1,500 | |
| Contingency (≈4%) | 2,000 | |
| **Total** | **50,000** | |

Co-financing: founder's in-kind time and existing MVP codebase (not costed). `[TBC: any other co-funding]`

---

## 10. Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| SACCOs unwilling to share historical data even under DPPA-compliant terms | Medium | Federated design means raw data never leaves the institution; retrospective validation (A2) can run on-premises with only aggregate results exported. Start with institutions already digitised. |
| Real fraud typologies differ from simulation; performance drops | Medium | This is precisely what Stage 0 tests; the rule-based MVP provides a floor that works regardless. |
| High false-positive rate overwhelms small SACCO staff | Medium–High | Threshold tuning on real data; alerts ranked and capped per week; measure investigation burden as an outcome. |
| Regulatory objection to a shared model hub | Low | Early engagement with UMRA; hub hosted in Uganda; CRB regulations as precedent. |
| Detection tool changes staff behaviour before evaluation (Hawthorne / deterrence) | Certain | Treat deterrence as a legitimate mechanism; randomisation at institution level captures it; measure behavioural indicators explicitly. |
| Applicant entity not eligible | — | Confirm registration before submission; consider a university-led consortium if needed. |

---

## 11. Timeline (Stage 0)

```
Month:        1   2   3   4   5   6   7   8   9
A1 MoUs       ███████████
A2 Real data      ███████████████████
A3 Baselines      ███████████████████
A4 Fed PoC                ███████████████████
A5 Eval design        ███████████████████████████
A6 Cost model                         ███████████
A7 Gender note                    ███████████████
Stage 1 application drafted                   ███
```

---

## 12. Alignment with FID selection criteria

| FID criterion | How this proposal meets it | Gap closed by Stage 0 |
|---|---|---|
| **Impact on people living in poverty** | Protects savings and credit access of ~18M mostly rural, low-income SACCO members; prevents institutional collapse that wipes out savings. | Baseline fraud-loss and member-exposure data (A3, A7). |
| **Cost-effectiveness vs. existing approaches** | Automated 100% coverage vs. manual audit of 5–10% of loans; marginal cost per institution is small relative to 2–5% annual losses. | Actual unit costs and loss-averted estimates (A6). |
| **Potential for scale and sustainability** | Federated hub designed as sector infrastructure (UMRA/UCSCU); open-source integration (Tazama); regional replicability. | Regulator and apex-body engagement (A1). |
| **Innovation** | First federated-learning fraud detection for SACCOs/MFIs in Africa; solves data scarcity and privacy-law constraints together. | — (established in the paper) |
| **Readiness for the requested stage** | Stage 0 is for promising applications that need preparation before a pilot; the MVP is prototyped and the federated design is published. | Real-data validation (A2, A4). |
| **Rigorous evaluation with a counterfactual** | Institution-level cluster RCT with phased roll-out proposed (§5). | Research partner and pre-registered design (A5). |
| **Priority sectors** | Not education/health/climate directly; **gender equality** angle via women's disproportionate reliance on SACCOs — to be substantiated. | Gender analysis (A7). |

---

## 13. Supporting materials in this repository

- `docs/FedFraudShield_DSA2026_Paper_v3.pdf` — technical paper with architecture, DPPA analysis and simulation results.
- `mvp/`, `mvp-fast/` — working FraudShield prototype (browser-based; accepts any CSV/Excel export).
- `backend/` — Python detection engine (rule-based + Isolation Forest / gradient boosting) and smart column-mapping module.
- `demo financial data/` — synthetic loan datasets used for demonstrations.

---

## 14. Pre-submission checklist

- [ ] Confirm legal entity, registration documents and bank account for FraudShield Uganda
- [ ] Re-read the current FID call guide and rules; confirm Stage 0 ceiling, duration and eligible costs
- [ ] Secure a letter of intent from at least one research partner
- [ ] Secure letters of intent from 3–5 SACCOs/MFIs
- [ ] Obtain a UMRA and/or UCSCU letter of support (or at least a meeting record)
- [ ] Replace every `[TBC]` above
- [ ] Verify all statistics cited (PROFIRA 2021, MTIC sector figures, ACFE 2024) and attach references
- [ ] Prepare 2-page summary and budget in FID's online application format
