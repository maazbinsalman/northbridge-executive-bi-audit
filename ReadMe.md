# 📊 Northbridge Group — Executive Performance & Financial Leakage Audit

An end-to-end Business Intelligence and Forensic Financial Analytics project investigating top-line revenue expansion vs. severe gross margin compression across a £24M professional services portfolio[cite: 3, 4].

---

## 📌 Executive Summary

Despite achieving **+15.79% YoY top-line revenue growth** (expanding from £21.03M to £24.35M in FY2025), Northbridge Group experienced a **-34.96% collapse in Gross Profit** (falling from £7.55M to £4.91M)[cite: 3]. 

Direct delivery labor costs escalated by **+44.22%**, compressing Group Gross Margin from **35.90% down to 20.17%** (and **12.72%** when contractor liabilities are imputed)[cite: 3].

## 🔎 Key Audit Findings & Root Causes

1. **Service Line Profit Leakage:** The *Data & Analytics* practice generated £1.67M in revenue across 36,418 delivery hours at an unviable **8.66% Gross Margin** (£144.9K profit), severely cannibalizing group margins[cite: 3].
2. **Uncosted Contractor Liabilities:** 41,222 delivery hours (8.58% of total volume) were logged by contractors with $NULL cost rates in source timesheets[cite: 4]. Grade-weighted imputation models revealed an additional £1.81M in unrecorded direct costs[cite: 3].
3. **General Ledger Reconciliation Timing Lag:** Invoicing system revenue exceeded GL recognized revenue by **+£2.04M (+9.14%)**, concentrated in subsidiary `NB-01` (+£1.89M / +24.10%) due to Q1 negative ledger adjustments and deferred revenue reversals[cite: 3, 4].

---

## 🛠️ Architecture & Technical Stack

* **Data Engineering & Extraction:** Python (`pandas`, `sqlite3`) used for automated data ingestion, white-space cleaning, entity code standardization, and contractor rate imputation algorithms[cite: 1, 4].
* **Dimensional Modeling:** Formatted a 3NF relational schema into an optimized **Star Schema** (`dim_entities`, `dim_clients`, `dim_projects`, `dim_staff`, `dim_date`, `fact_invoices`, `fact_timesheets`, `fact_gl_revenue`)[cite: 3, 4].
* **Advanced DAX & Metrics:** Implemented dynamic measure tables covering time-intelligence, variance calculations, and dual-margin perspectives (Known vs. Imputed)[cite: 3].
* **UI/UX Executive Design:** Designed a 2-page C-suite canvas adhering to visual hierarchy, corporate color palettes, and zero-clutter principles[cite: 3].

---

## 📁 Repository Deliverables

- 📄 `NorthBridge - Executive Memorandum.pdf` — Strategic 1-page C-suite briefing on intervention options and operational governance[cite: 3].
- 📊 `PowerBI Dashboard.pbix` — Interactive two-page executive report file[cite: 3].
- 📜 `01_schema_transformation.sql` — Data cleaning, Star Schema transformation, and accounting audit queries[cite: 4].
- 🧮 `dax_measures.dax` — Structured DAX calculation formulas[cite: 3].
- 🖥️ `NorthBridge - PowerBI Dashboard (PDF).pdf` — High-resolution exported presentation canvas[cite: 3].
- 📊 `Northbridge_FY2025_Executive_Deck.pptx` — C-suite executive slide deck.

---

## 👤 Author & Contact

**Data Specialist / Analytics Engineer**  
*Specializing in SQL, Power BI, Python, and Financial Data Analytics for US/UK clients.*