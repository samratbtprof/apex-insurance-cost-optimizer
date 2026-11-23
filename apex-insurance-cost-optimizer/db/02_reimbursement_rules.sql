-- Reimbursement rules (reference set, synthetic). The generator applies the same logic in Python.

INSERT INTO reimbursement_rules (rule_code, description, rule_type, param_value) VALUES
 ('R01_OFF_FORMULARY',  'Drug not on plan formulary: reject claim',                         'REJECT',    NULL);
INSERT INTO reimbursement_rules (rule_code, description, rule_type, param_value) VALUES
 ('R02_QTY_EXCEEDS_RX', 'Dispensed quantity above prescribed quantity: pay prescribed qty only','SHORT_PAY', NULL);
INSERT INTO reimbursement_rules (rule_code, description, rule_type, param_value) VALUES
 ('R03_GENERIC_CAP',    'Generic equivalent exists: reimburse branded drug at generic price plus tolerance %','SHORT_PAY', 10);
INSERT INTO reimbursement_rules (rule_code, description, rule_type, param_value) VALUES
 ('R04_LATE_CLAIM',     'Claim filed more than N days after dispense: reject',               'REJECT',    30);
INSERT INTO reimbursement_rules (rule_code, description, rule_type, param_value) VALUES
 ('R05_NEAR_EXPIRY',    'Batch expiring within N days of dispense: flag for review',         'FLAG',      30);
COMMIT;
