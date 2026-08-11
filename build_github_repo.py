import os

# Define GitHub Directory Structure
folders = [
    "northbridge-executive-bi-audit",
    "northbridge-executive-bi-audit/data",
    "northbridge-executive-bi-audit/sql",
    "northbridge-executive-bi-audit/dax",
    "northbridge-executive-bi-audit/powerbi",
    "northbridge-executive-bi-audit/docs",
    "northbridge-executive-bi-audit/docs/screenshots"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"📁 Created folder: {folder}")

# 1. SQL Transformation File
sql_content = """-- ====================================================================
-- NORTHBRIDGE GROUP: SQL ETL & DATAWAREHOUSE MODELING
-- Purpose: Whitespace cleaning, service line unification, & contractor cost imputation
-- Database Engine: SQLite / Relational Schema
-- ====================================================================

-- 1. CLEANING DIMENSION ENTITIES
CREATE TABLE IF NOT EXISTS dim_entities AS
SELECT 
    TRIM(entity_code) AS entity_code,
    TRIM(entity_name) AS entity_name,
    service_focus,
    region,
    currency
FROM entities;

-- 2. CLEANING & UNIFYING DIMENSION PROJECTS
CREATE TABLE IF NOT EXISTS dim_projects AS
SELECT 
    project_id,
    client_id,
    TRIM(entity_code) AS entity_code,
    project_name,
    CASE 
        WHEN service_line = 'M&E' THEN 'Mechanical & Electrical'
        WHEN service_line = 'Consulting' THEN 'Advisory'
        ELSE service_line
    END AS clean_service_line,
    start_date,
    end_date,
    contract_value,
    status
FROM projects;

-- 3. FACT TIMESHEETS & CONTRACTOR COST RATE IMPUTATION
-- Imputes missing $NULL contractor cost rates using grade-level permanent averages
CREATE TABLE IF NOT EXISTS fact_timesheets_clean AS
WITH perm_grade_averages AS (
    SELECT 
        s.grade,
        AVG(t.cost_rate) AS avg_perm_cost_rate
    FROM timesheets t
    JOIN staff s ON t.staff_id = s.staff_id
    WHERE s.engagement_type = 'Permanent' AND t.cost_rate IS NOT NULL
    GROUP BY s.grade
)
SELECT 
    t.timesheet_id,
    t.project_id,
    t.staff_id,
    t.week_commencing,
    t.hours,
    t.charge_rate,
    t.cost_rate AS known_cost_rate,
    COALESCE(t.cost_rate, pga.avg_perm_cost_rate, 0.0) AS imputed_cost_rate,
    (t.hours * COALESCE(t.cost_rate, 0.0)) AS known_cost_gbp,
    (t.hours * COALESCE(t.cost_rate, pga.avg_perm_cost_rate, 0.0)) AS imputed_cost_gbp
FROM timesheets t
JOIN staff s ON t.staff_id = s.staff_id
LEFT JOIN perm_grade_averages pga ON s.grade = pga.grade;

-- 4. GENERAL LEDGER RECONCILIATION QUERY
-- Identifies Invoiced Revenue vs GL Recognised Revenue Discrepancies
SELECT 
    e.entity_code,
    e.entity_name,
    SUM(i.invoice_amount) AS total_invoiced_revenue,
    gl.gl_revenue AS total_gl_recognised_revenue,
    (SUM(i.invoice_amount) - gl.gl_revenue) AS billing_vs_gl_variance_gbp,
    ROUND(((SUM(i.invoice_amount) - gl.gl_revenue) / gl.gl_revenue) * 100, 2) AS variance_percentage
FROM dim_entities e
JOIN dim_projects p ON e.entity_code = p.entity_code
JOIN invoices i ON p.project_id = i.project_id
LEFT JOIN (
    SELECT TRIM(entity_code) AS entity_code, SUM(revenue_recognised) AS gl_revenue 
    FROM gl_revenue_summary 
    WHERE period_month LIKE '2025%'
    GROUP BY TRIM(entity_code)
) gl ON e.entity_code = gl.entity_code
WHERE i.invoice_date LIKE '2025%'
GROUP BY e.entity_code, e.entity_name;
"""

with open("northbridge-executive-bi-audit/sql/01_schema_transformation.sql", "w", encoding="utf-8") as f:
    f.write(sql_content)

# 2. DAX Measures Library
dax_content = """// ====================================================================
// DAX MEASURES LIBRARY — NORTHBRIDGE GROUP EXECUTIVE CANVAS
// Storage Table: _Measures
// ====================================================================

// --- GROUP 1: CORE REVENUE & COST ---

Total Invoiced Revenue = 
SUM(fact_invoices[invoice_amount])

Total Delivery Hours = 
SUM(fact_timesheets[hours])

Permanent Hours = 
CALCULATE(
    SUM(fact_timesheets[hours]),
    dim_staff[engagement_type] = "Permanent"
)

Contractor Hours = 
CALCULATE(
    SUM(fact_timesheets[hours]),
    dim_staff[engagement_type] = "Contract"
)

Contractor Ratio % = 
DIVIDE([Contractor Hours], [Total Delivery Hours], 0)

Known Delivery Cost = 
SUM(fact_timesheets[known_cost_gbp])

Imputed Delivery Cost = 
SUM(fact_timesheets[imputed_cost_gbp])


// --- GROUP 2: GROSS MARGIN & PROFITABILITY ---

Known Gross Margin (£) = 
[Total Invoiced Revenue] - [Known Delivery Cost]

Known Gross Margin (%) = 
DIVIDE([Known Gross Margin (£)], [Total Invoiced Revenue], 0)

Imputed Gross Margin (£) = 
[Total Invoiced Revenue] - [Imputed Delivery Cost]

Imputed Gross Margin (%) = 
DIVIDE([Imputed Gross Margin (£)], [Total Invoiced Revenue], 0)

YoY Margin Compression = 
VAR PrevYearMargin = 
    CALCULATE([Known Gross Margin (%)], SAMEPERIODLASTYEAR(dim_date[full_date]))
RETURN
    [Known Gross Margin (%)] - PrevYearMargin


// --- GROUP 3: GENERAL LEDGER RECONCILIATION ---

GL Recognised Revenue = 
SUM(fact_gl_revenue[revenue_recognised])

Billing vs GL Variance (£) = 
[Total Invoiced Revenue] - [GL Recognised Revenue]

Billing vs GL Variance (%) = 
DIVIDE([Billing vs GL Variance (£)], [GL Recognised Revenue], 0)
"""

with open("northbridge-executive-bi-audit/dax/dax_measures.dax", "w", encoding="utf-8") as f:
    f.write(dax_content)

# 3. Executive CEO Memorandum
memo_content = """# EXECUTIVE MEMORANDUM

**TO:** Chief Executive Officer, Northbridge Group  
**FROM:** Lead Business Analyst / Analytics Engineer, Power House Unit  
**DATE:** August 10, 2026  
**SUBJECT:** FY2025 Performance Interrogation, Profit Compression & Operational Governance Plan  

---

### 1. EXECUTIVE SUMMARY & CORE FINDINGS
Northbridge Group experienced severe profit erosion in FY2025 despite expanding headline revenue. While total invoiced revenue grew by **+15.79%** (from £21.03M to £24.35M), direct delivery labor costs surged by **+44.22%** (from £13.48M to £19.44M). Consequently, Gross Profit collapsed by **-34.96%** (from £7.55M down to £4.91M), compressing Gross Margin from **35.90% to 20.17%** (and down to **12.72%** when contractor costs are imputed at permanent grade averages).
