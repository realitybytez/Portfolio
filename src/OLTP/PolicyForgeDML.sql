COPY party
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\party.csv'
WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');

COPY policy
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\policy.csv'
WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');

COPY party_policy_association
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\party_policy_association.csv'
WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');

COPY transaction
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\transaction.csv'
WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');

COPY address
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\address.csv'
WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');

COPY contact
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\contact.csv'
WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');

COPY coverage
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\coverage.csv'
WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');

COPY premium_detail
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\premium_detail.csv'
WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');

COPY contents
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\contents.csv'
WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');

COPY occupancy
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\occupancy.csv'
WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');

COPY property
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\property.csv'
WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');

COPY roof_material_type
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\roof_material_type.csv'
WITH (FORMAT CSV, HEADER FALSE, DELIMITER ',');

COPY property_occupation_type
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\property_occupation_type.csv'
WITH (FORMAT CSV, HEADER FALSE, DELIMITER ',');

COPY property_type
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\property_type.csv'
WITH (FORMAT CSV, HEADER FALSE, DELIMITER ',');

COPY address_type
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\address_type.csv'
WITH (FORMAT CSV, HEADER FALSE, DELIMITER ',');

COPY transaction_status_type
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\transaction_status_type.csv'
WITH (FORMAT CSV, HEADER FALSE, DELIMITER ',');

COPY transaction_type
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\transaction_type.csv'
WITH (FORMAT CSV, HEADER FALSE, DELIMITER ',');

COPY coverage_type
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\coverage_type.csv'
WITH (FORMAT CSV, HEADER FALSE, DELIMITER ',');

COPY wall_material_type
FROM 'C:\Users\User\Desktop\Portfolio\src\OLTP\output\wall_material_type.csv'
WITH (FORMAT CSV, HEADER FALSE, DELIMITER ',');
