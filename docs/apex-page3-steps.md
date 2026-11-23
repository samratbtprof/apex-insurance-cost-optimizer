# Page 3 "Drug wastage": steps

Goal: show how much stock value is written off, why (expired, overstock, damaged), when, and which drugs. Uses the view `v_drug_wastage` (columns: WASTAGE_MONTH, DRUG_NAME, REASON, QTY, WASTAGE_VALUE).

Expected numbers (computed on the synthetic CSVs in SQLite; not yet run on Oracle):
- 192 write-offs, 41,892 units, total value 1,942,195.60
- EXPIRED: 105 rows, 992,210. OVERSTOCK: 62 rows, 772,016. DAMAGED: 25 rows, 177,970
- Months: 2025-01 to 2025-12 (12 months)
- Top drugs by value: Insulin Glargine (generic) 622,200; Insulin Glargine (brand) 615,720; Specialty Brand Y 144,760; Specialty Brand X 131,195; Azithromycin (generic) 65,468

## A. Create the page
App Builder, Create Page, Blank Page. Name `Drug wastage`, add to navigation menu. Open it in Page Designer. Set the breadcrumb label (or remove the breadcrumb) as you did on page 1.

## B. Region A: key figures (Cards)
Same settings as page 1 region A (Title column VALUE, Subtitle column TITLE, 4-column grid). SQL:

```sql
SELECT 'Total wastage value' title, TO_CHAR(SUM(wastage_value),'FM99G99G99G990') value FROM v_drug_wastage
UNION ALL
SELECT 'Units written off', TO_CHAR(SUM(qty),'FM99G99G99G990') FROM v_drug_wastage
UNION ALL
SELECT 'Write-offs', TO_CHAR(COUNT(*),'FM99G990') FROM v_drug_wastage
UNION ALL
SELECT 'Expired share of value',
       TO_CHAR(100 * SUM(CASE WHEN reason='EXPIRED' THEN wastage_value END) / SUM(wastage_value),'FM990.0') || '%'
  FROM v_drug_wastage
```
Expected cards: 19,42,196 / 41,892 / 192 / 51.1%.

## C. Region B: wastage by reason (Chart, Bar, horizontal)
```sql
SELECT reason label, ROUND(SUM(wastage_value),0) value
  FROM v_drug_wastage GROUP BY reason ORDER BY 2 DESC
```
Label LABEL, Value VALUE. Layout: Start New Row on, Column Span 6.

## D. Region C: wastage by month, stacked by reason (Chart, Bar vertical, Stack on)
```sql
SELECT TO_CHAR(wastage_month,'YYYY-MM') month_label,
       reason series_name,
       ROUND(SUM(wastage_value),0) value
  FROM v_drug_wastage
 GROUP BY wastage_month, reason
 ORDER BY wastage_month, reason
```
Column Mapping: Series Name SERIES_NAME, Label MONTH_LABEL, Value VALUE. Layout: Start New Row off, Column Span 6. A month with no write-off for a reason simply has no segment.

## E. Region D: top drugs by wastage value (Chart, Bar, horizontal)
```sql
SELECT drug_name label, ROUND(SUM(wastage_value),0) value
  FROM v_drug_wastage GROUP BY drug_name ORDER BY 2 DESC
 FETCH FIRST 10 ROWS ONLY
```
Label LABEL, Value VALUE. Layout: Start New Row on, Column Span 12. Turn the legend off on the single-series charts.

## F. Data note
Add a Static Content region at the bottom: `Synthetic data. Reference implementation. Not client data.`

## Note for the case study
Two Insulin Glargine lines make up about 64% of the synthetic wastage value. That comes from how the generator sets stock levels and costs, not from a finding. Do not describe it as an insight from the hospital's data.
