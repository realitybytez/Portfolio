\copy party FROM './output/party.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy policy FROM './output/policy.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy party_policy_association FROM './output/party_policy_association.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy transaction FROM './output/transaction.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy address FROM './output/address.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy contact FROM './output/contact.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy coverage FROM './output/coverage.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy premium_detail FROM './output/premium_detail.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy contents FROM './output/contents.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy occupancy FROM './output/occupancy.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy property FROM './output/property.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy roof_material_type FROM './output/roof_material_type.csv' (FORMAT CSV, HEADER FALSE, DELIMITER ',');
\copy property_occupation_type FROM './output/property_occupation_type.csv' (FORMAT CSV, HEADER FALSE, DELIMITER ',');
\copy property_type FROM './output/property_type.csv' (FORMAT CSV, HEADER FALSE, DELIMITER ',');
\copy address_type FROM './output/address_type.csv' (FORMAT CSV, HEADER FALSE, DELIMITER ',');
\copy transaction_status_type FROM './output/transaction_status_type.csv' (FORMAT CSV, HEADER FALSE, DELIMITER ',');
\copy transaction_type FROM './output/transaction_type.csv' (FORMAT CSV, HEADER FALSE, DELIMITER ',');
\copy coverage_type FROM './output/coverage_type.csv' (FORMAT CSV, HEADER FALSE, DELIMITER ',');
\copy wall_material_type FROM './output/wall_material_type.csv' (FORMAT CSV, HEADER FALSE, DELIMITER ',');
