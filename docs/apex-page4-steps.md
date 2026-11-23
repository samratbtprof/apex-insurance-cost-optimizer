# Page 4 "Generic opportunities": steps

Goal: show which branded drugs were dispensed although a cheaper generic in the same group existed, and how much that cost. This is the GENERIC_MISSED cause from page 1, drug by drug. It is the page a pharmacy lead would use to decide which substitutions to push first.

Expected numbers (computed on the synthetic CSVs in SQLite; not yet run on Oracle): 10 branded drugs, 1,787 claims, total 696,889 (matches page 1).
Top rows: Insulin Glargine (brand) 204 claims, 475,853; Azithromycin (brand) 162, 58,877; Telmisartan (brand) 208, 31,296; Amoxicillin (brand) 159, 27,841; Atorvastatin (brand) 184, 25,155.

## A. Create the page
Create Page, Interactive Report. Name `Generic opportunities`, add to the navigation menu, source SQL Query:

```sql
SELECT dm.drug_name       AS branded_drug,
       dm.unit_cost       AS brand_unit_cost,
       (SELECT MIN(g.unit_cost) FROM drug_master g
         WHERE g.generic_group = dm.generic_group AND g.is_generic = 'Y') AS generic_unit_cost,
       COUNT(*)           AS claims,
       ROUND(SUM(l.leakage_amount),0) AS potential_saving
  FROM v_claim_leakage l
  JOIN claims c            ON c.claim_id = l.claim_id
  JOIN dispense_records ds ON ds.dispense_id = c.dispense_id
  JOIN drug_master dm      ON dm.drug_id = ds.drug_id
 WHERE l.leakage_type = 'GENERIC_MISSED'
 GROUP BY dm.drug_name, dm.generic_group, dm.unit_cost
 ORDER BY potential_saving DESC
```

## B. Check
- 10 rows. Open the menu, Data, Aggregate: Sum of POTENTIAL_SAVING should be 696,889 and Sum of CLAIMS 1,787.
- Insulin Glargine (brand) is first: brand unit cost 420, cheapest generic 340, 204 claims, 475,853.

## C. Tidy
Headings: Branded drug, Brand unit cost, Cheapest generic unit cost, Claims, Potential saving. Save as the Primary report.

## Note for the case study
Potential saving means what the same dispenses would have cost at the cheapest generic's price. It assumes the generic was clinically suitable and in stock, which a prescriber and the pharmacy decide. Say "potential", never "saving achieved". Insulin Glargine is about 68% of the total only because of how the generator priced it.
