-- providers: rows 1 to 5 of 5 (synthetic data)
BEGIN
INSERT INTO providers (provider_id, provider_name, provider_type) VALUES (1, 'Synthetic General Hospital', 'HOSPITAL');
INSERT INTO providers (provider_id, provider_name, provider_type) VALUES (2, 'Synthetic City Clinic', 'CLINIC');
INSERT INTO providers (provider_id, provider_name, provider_type) VALUES (3, 'Synthetic Care Pharmacy', 'PHARMACY');
INSERT INTO providers (provider_id, provider_name, provider_type) VALUES (4, 'Synthetic Metro Hospital', 'HOSPITAL');
INSERT INTO providers (provider_id, provider_name, provider_type) VALUES (5, 'Synthetic Community Clinic', 'CLINIC');
END;
/
COMMIT;
