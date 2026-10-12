-- Credit Risk and Loan Approval Analysis
-- Database: data/processed/loan_data.db (SQLite)
-- Table: customers (one row per customer)
-- Risk categories: P1 = lowest risk ... P4 = highest risk


-- Q1. How many customers are in each risk category?
SELECT
    approved_flag,
    COUNT(*) AS total_customers,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers), 2) AS pct_of_customers
FROM customers
GROUP BY approved_flag
ORDER BY approved_flag;


-- Q2. Average credit score, income and age for each risk category
SELECT
    approved_flag,
    ROUND(AVG(credit_score), 1)      AS avg_credit_score,
    ROUND(AVG(netmonthlyincome), 0)  AS avg_income,
    ROUND(AVG(age), 1)               AS avg_age
FROM customers
GROUP BY approved_flag
ORDER BY approved_flag;


-- Q3. Risk category split by gender
SELECT
    gender,
    approved_flag,
    COUNT(*) AS total_customers
FROM customers
GROUP BY gender, approved_flag
ORDER BY gender, approved_flag;


-- Q4. Percentage of low risk (P1) customers by education level
SELECT
    education,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN approved_flag = 'P1' THEN 1 ELSE 0 END) AS p1_customers,
    ROUND(SUM(CASE WHEN approved_flag = 'P1' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS p1_pct
FROM customers
GROUP BY education
ORDER BY p1_pct DESC;


-- Q5. Income band vs risk: share of high risk customers (P3 + P4)
SELECT
    income_band,
    COUNT(*) AS total_customers,
    ROUND(SUM(CASE WHEN approved_flag IN ('P3', 'P4') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS high_risk_pct
FROM customers
GROUP BY income_band
ORDER BY high_risk_pct DESC;


-- Q6. Age group vs risk: share of high risk customers (P3 + P4)
SELECT
    age_group,
    COUNT(*) AS total_customers,
    ROUND(SUM(CASE WHEN approved_flag IN ('P3', 'P4') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS high_risk_pct
FROM customers
GROUP BY age_group
ORDER BY age_group;


-- Q7. Missed payments per loan account for each risk category
-- (P1 customers hold more loan accounts, so we divide by total accounts)
SELECT
    approved_flag,
    SUM(tot_missed_pmnt) AS total_missed,
    SUM(total_tl)        AS total_accounts,
    ROUND(SUM(tot_missed_pmnt) * 1.0 / SUM(total_tl), 3) AS missed_per_account
FROM customers
GROUP BY approved_flag
ORDER BY approved_flag;


-- Q8. Do customers who enquire a lot end up in higher risk categories?
SELECT
    approved_flag,
    ROUND(AVG(enq_l6m), 2)  AS avg_enquiries_6m,
    ROUND(AVG(enq_l12m), 2) AS avg_enquiries_12m,
    ROUND(AVG(tot_enq), 2)  AS avg_total_enquiries
FROM customers
GROUP BY approved_flag
ORDER BY approved_flag;


-- Q9. Which first product enquired has the most low risk customers?
SELECT
    first_prod_enq2 AS first_product,
    COUNT(*) AS total_customers,
    ROUND(SUM(CASE WHEN approved_flag = 'P1' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS p1_pct
FROM customers
GROUP BY first_prod_enq2
ORDER BY p1_pct DESC;


-- Q10. Credit score band vs risk category (count)
SELECT
    score_band,
    SUM(CASE WHEN approved_flag = 'P1' THEN 1 ELSE 0 END) AS p1,
    SUM(CASE WHEN approved_flag = 'P2' THEN 1 ELSE 0 END) AS p2,
    SUM(CASE WHEN approved_flag = 'P3' THEN 1 ELSE 0 END) AS p3,
    SUM(CASE WHEN approved_flag = 'P4' THEN 1 ELSE 0 END) AS p4
FROM customers
GROUP BY score_band
ORDER BY score_band;


-- Q11. Top 10 highest income customers who are in P3 or P4
SELECT
    prospectid, age, education, netmonthlyincome, credit_score, approved_flag
FROM customers
WHERE approved_flag IN ('P3', 'P4')
ORDER BY netmonthlyincome DESC
LIMIT 10;


-- Q12. Rank education levels by average credit score (window function)
SELECT
    education,
    ROUND(AVG(credit_score), 1) AS avg_score,
    RANK() OVER (ORDER BY AVG(credit_score) DESC) AS score_rank
FROM customers
GROUP BY education;


-- Q13. Customers with more loan accounts than the average (subquery)
SELECT
    approved_flag,
    COUNT(*) AS customers_above_avg_accounts
FROM customers
WHERE total_tl > (SELECT AVG(total_tl) FROM customers)
GROUP BY approved_flag
ORDER BY approved_flag;


-- Q14. Home loan holders vs others: average credit score and risk mix
SELECT
    CASE WHEN home_tl > 0 THEN 'Has home loan' ELSE 'No home loan' END AS home_loan_status,
    COUNT(*) AS total_customers,
    ROUND(AVG(credit_score), 1) AS avg_credit_score,
    ROUND(SUM(CASE WHEN approved_flag = 'P1' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS p1_pct
FROM customers
GROUP BY home_loan_status;
