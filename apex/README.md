# apex/ : application export

`f43742.sql` is a standard export (Oracle APEX 26.2.1) of the reference app "Insurance Cost Optimizer": five pages (Leakage overview, Claim drill-down, Drug wastage, Generic opportunities, Reimbursement rules plus its form page).

Scrubbed before publishing: the developer's email address is replaced by `DEVELOPER@EXAMPLE.COM` and the workspace schema name by `YOUR_SCHEMA`. The internal numeric workspace id is still in the file; it is overridden when you import into your own workspace.

## To import
1. Create the tables and load the synthetic data first (see `docs/apex-build-guide.md`, Part 1). The pages read those tables and the views `v_claim_leakage` and `v_drug_wastage`.
2. App Builder, Import, choose `f43742.sql`. When asked for the parsing schema, choose your own workspace schema.
3. If application id 43742 is taken in your workspace, choose a new id.

Not verified: this scrubbed file has not been re-imported into a fresh workspace. The unscrubbed original was exported from the owner's own workspace and ran there. Please tell the repo owner if an import fails.
