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