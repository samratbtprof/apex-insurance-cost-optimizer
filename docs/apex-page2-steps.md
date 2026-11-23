# Page 2 "Claim drill-down": steps

Goal: a claims manager sees every claim that leaked money, with the cause, the amount lost, and the rule that applied. Filter by cause and status; click a row to see the claim.

## A. Create the page
1. App Builder, your app, Create Page, Report, Interactive Report. (If your menu says only "Blank Page", choose that and add an Interactive Report region.)
2. Page name: `Claim drill-down`. Add to navigation menu: yes. Next, source: SQL Query, paste the SQL below, Create Page.

```sql
SELECT c.claim_id,
       c.claim_date,
       p.provider_name,
       dm.drug_name,
       l.leakage_type,
       c.claimed_amount,
       c.approved_amount,
       ROUND(l.leakage_amount,2) AS amount_lost,
       c.status,
       c.rule_code
  FROM v_claim_leakage l
  JOIN claims c            ON c.claim_id = l.claim_id
  JOIN dispense_records ds ON ds.dispense_id = c.dispense_id
  JOIN drug_master dm      ON dm.drug_id = ds.drug_id
  JOIN prescriptions rx    ON rx.rx_id = ds.rx_id
  JOIN providers p         ON p.provider_id = rx.provider_id
```

## B. Run and check
1. Save, Run. Open the Actions menu on the report, choose Select Rows or look at the row count at the bottom.
2. Expected: 3,224 rows in total.
3. Actions, Filter, Column LEAKAGE_TYPE equals OFF_FORMULARY: expect 373 rows. GENERIC_MISSED: 1,787. REIMBURSEMENT_LOSS: 366. OVER_DISPENSE: 698.
4. Actions, Format, Control Break or Aggregate: sum of AMOUNT_LOST should be 2,496,022.62 (the aggregate may show 2,496,023).

## C. Tidy
- Rename the page title and breadcrumb label to `Claim drill-down` (the same two places as on page 1).
- Change column headings to plain words: AMOUNT_LOST to `Amount lost`, RULE_CODE to `Rule applied`.
- Optional: Actions, Save Report, Primary, so everyone sees the same default view.

## What to send back
A screenshot of the report, and the row counts from step B3. If a count differs, send me the number you see.

Note: a blank RULE_CODE means the claim was approved in full (no rule fired), yet the view still counts a loss, for example a branded drug paid when a cheaper generic existed. Those rows are the point of the page: money lost that no rejection ever flagged.
