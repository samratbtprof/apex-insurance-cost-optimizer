-- insurance_plans: rows 1 to 3 of 3 (synthetic data)
BEGIN
INSERT INTO insurance_plans (plan_id, plan_name, annual_premium, copay_pct, formulary_required) VALUES (1, 'Basic', 6000, 20, 'Y');
INSERT INTO insurance_plans (plan_id, plan_name, annual_premium, copay_pct, formulary_required) VALUES (2, 'Standard', 12000, 10, 'Y');
INSERT INTO insurance_plans (plan_id, plan_name, annual_premium, copay_pct, formulary_required) VALUES (3, 'Premium', 24000, 5, 'N');
COMMIT;
END;
