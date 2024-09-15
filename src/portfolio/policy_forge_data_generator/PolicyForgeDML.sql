\copy source.party FROM './output/party.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy source.policy FROM './output/policy.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy source.party_policy_association FROM './output/party_policy_association.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy source.transaction FROM './output/transaction.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy source.address FROM './output/address.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy source.contact FROM './output/contact.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy source.coverage FROM './output/coverage.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy source.premium_detail FROM './output/premium_detail.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy source.contents FROM './output/contents.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy source.occupancy FROM './output/occupancy.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy source.property FROM './output/property.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\copy source.roof_material_type FROM './output/roof_material_type.csv' (FORMAT CSV, HEADER FALSE, DELIMITER ',');
\copy source.property_occupation_type FROM './output/property_occupation_type.csv' (FORMAT CSV, HEADER FALSE, DELIMITER ',');
\copy source.property_type FROM './output/property_type.csv' (FORMAT CSV, HEADER FALSE, DELIMITER ',');
\copy source.address_type FROM './output/address_type.csv' (FORMAT CSV, HEADER FALSE, DELIMITER ',');
\copy source.transaction_status_type FROM './output/transaction_status_type.csv' (FORMAT CSV, HEADER FALSE, DELIMITER ',');
\copy source.transaction_type FROM './output/transaction_type.csv' (FORMAT CSV, HEADER FALSE, DELIMITER ',');
\copy source.coverage_type FROM './output/coverage_type.csv' (FORMAT CSV, HEADER FALSE, DELIMITER ',');
\copy source.wall_material_type FROM './output/wall_material_type.csv' (FORMAT CSV, HEADER FALSE, DELIMITER ',');
