# Page "Reimbursement rules" (rules admin): steps

Goal: show the versioned reimbursement rules and let a user add a new version. Table: `reimbursement_rules` (RULE_ID, RULE_CODE, VERSION_NO, EFFECTIVE_FROM, EFFECTIVE_TO, DESCRIPTION, RULE_TYPE, PARAM_VALUE, ACTIVE_YN). The reference data has 5 rules, version 1: R01_OFF_FORMULARY, R02_QTY_EXCEEDS_RX, R03_GENERIC_CAP, R04_LATE_CLAIM, R05_NEAR_EXPIRY.

## A. Create the report and form
1. Create Page, choose **Report with Form** (or Form, Report and Form; the label varies).
2. Report type: Interactive Report. Report page name `Reimbursement rules`, form page name `Rule details`. Add the report to the navigation menu.
3. Data source: Table, `REIMBURSEMENT_RULES`. Primary key column: `RULE_ID`.
4. Form columns: select all. Create.
5. Run. You should see 5 rows. Open one with the edit pencil to check the form.

## B. Tidy
- Headings: Rule code, Version, Effective from, Effective to, Description, Type, Parameter, Active.
- On the form, make `RULE_ID` hidden or display only. Set `RULE_TYPE` to a select list with values REJECT, SHORT_PAY, FLAG, and `ACTIVE_YN` to a switch (Y/N), if the wizard offered text fields.
- Add the note region: `Synthetic data. Reference implementation. Not client data.`

## C. What this page does not do (say so in the case study)
- The leakage view `v_claim_leakage` and the claim decisions in the synthetic data apply the rules in fixed code and in the generator. Editing a row here does **not** change any claim or any figure on the other pages.
- The delivered system kept rules per insurer, versioned, with a rule engine per insurer. The reference shows only the table and versions.
- There is no manager authorization or change log on this page. In the delivered system, edits needed a claims manager's temporary authorization and were logged. That is parked for section 5 together with `db/04_security_audit.sql`, which is an unrun sketch.

A page that edits rules but does not change results is a limitation, and it belongs in the repo README and section 5 as a known gap, not hidden.
