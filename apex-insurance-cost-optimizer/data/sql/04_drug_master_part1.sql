-- drug_master: rows 1 to 22 of 22 (synthetic data)
BEGIN
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (1, 'Metformin (brand)', 'Metformin', 'N', 9.0, 730, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (2, 'Metformin (generic)', 'Metformin', 'Y', 6.0, 730, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (3, 'Atorvastatin (brand)', 'Atorvastatin', 'N', 14.0, 730, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (4, 'Atorvastatin (generic)', 'Atorvastatin', 'Y', 9.0, 730, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (5, 'Amlodipine (brand)', 'Amlodipine', 'N', 8.0, 730, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (6, 'Amlodipine (generic)', 'Amlodipine', 'Y', 5.5, 730, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (7, 'Omeprazole (brand)', 'Omeprazole', 'N', 11.0, 540, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (8, 'Omeprazole (generic)', 'Omeprazole', 'Y', 7.0, 540, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (9, 'Azithromycin (brand)', 'Azithromycin', 'N', 38.0, 365, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (10, 'Azithromycin (generic)', 'Azithromycin', 'Y', 26.0, 365, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (11, 'Amoxicillin (brand)', 'Amoxicillin', 'N', 20.0, 365, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (12, 'Amoxicillin (generic)', 'Amoxicillin', 'Y', 13.0, 365, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (13, 'Telmisartan (brand)', 'Telmisartan', 'N', 16.0, 730, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (14, 'Telmisartan (generic)', 'Telmisartan', 'Y', 10.5, 730, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (15, 'Pantoprazole (brand)', 'Pantoprazole', 'N', 13.0, 540, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (16, 'Pantoprazole (generic)', 'Pantoprazole', 'Y', 8.5, 540, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (17, 'Cetirizine (brand)', 'Cetirizine', 'N', 5.0, 730, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (18, 'Cetirizine (generic)', 'Cetirizine', 'Y', 3.2, 730, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (19, 'Insulin Glargine (brand)', 'Insulin Glargine', 'N', 420.0, 365, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (20, 'Insulin Glargine (generic)', 'Insulin Glargine', 'Y', 340.0, 365, 'Y');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (21, 'Specialty Brand X', 'Specialty Brand X', 'N', 95.0, 365, 'N');
INSERT INTO drug_master (drug_id, drug_name, generic_group, is_generic, unit_cost, shelf_life_days, on_formulary) VALUES (22, 'Specialty Brand Y', 'Specialty Brand Y', 'N', 140.0, 365, 'N');
END;
/
COMMIT;
