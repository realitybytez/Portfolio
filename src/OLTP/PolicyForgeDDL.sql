CREATE DATABASE policy_forge_read_replica
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United States.1252'
    LC_CTYPE = 'English_United States.1252'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

DROP TABLE IF EXISTS policy CASCADE;
DROP TABLE IF EXISTS party CASCADE;
DROP TABLE IF EXISTS transaction CASCADE;
DROP TABLE IF EXISTS party_policy_association CASCADE;
DROP TABLE IF EXISTS address CASCADE;
DROP TABLE IF EXISTS contact CASCADE;
DROP TABLE IF EXISTS coverage CASCADE;
DROP TABLE IF EXISTS premium_detail CASCADE;
DROP TABLE IF EXISTS contents CASCADE;
DROP TABLE IF EXISTS occupancy CASCADE;
DROP TABLE IF EXISTS property CASCADE;

CREATE TABLE party (
   party_id INTEGER PRIMARY KEY,
   given_name VARCHAR(50) NOT NULL,
   surname VARCHAR(50) NOT NULL,
   role VARCHAR(20) NOT NULL,
   modified TIMESTAMP NOT NULL
);

CREATE TABLE policy (
   policy_id INTEGER PRIMARY KEY,
   policy_number VARCHAR(15) NOT NULL,
   channel VARCHAR(20) NOT NULL,
   inception TIMESTAMP NOT NULL,
   brand VARCHAR(30) NOT NULL,
   line_of_business VARCHAR(20) NOT NULL,
   modified TIMESTAMP NOT NULL
);

CREATE TABLE party_policy_association (
   party_policy_id INTEGER PRIMARY KEY,
   policy_id INTEGER NOT NULL,
   party_id INTEGER NOT NULL,
   modified TIMESTAMP NOT NULL,
   CONSTRAINT fk_party_policy_association_party FOREIGN KEY (party_id) REFERENCES party (party_id),
   CONSTRAINT fk_party_policy_association_policy FOREIGN KEY (policy_id) REFERENCES policy (policy_id)
);

CREATE TABLE transaction (
   transaction_id INTEGER PRIMARY KEY,
   policy_id INTEGER NOT NULL,
   transaction_type_key VARCHAR(3) NOT NULL,
   transaction_state_key VARCHAR(3) NOT NULL,
   sequence int NOT NULL,
   effective TIMESTAMP NOT NULL,
   expiration TIMESTAMP NOT NULL,
   modified TIMESTAMP NOT NULL,
   CONSTRAINT fk_transaction_policy FOREIGN KEY (policy_id) REFERENCES policy (policy_id)
);

CREATE TABLE address (
   address_id INTEGER PRIMARY KEY,
   address_key VARCHAR(3) NOT NULL,
   address_line VARCHAR(100) NOT NULL,
   suburb VARCHAR(100) NOT NULL,
   postcode VARCHAR(4) NOT NULL,
   state VARCHAR(3) NOT NULL,
   country VARCHAR(2) NOT NULL,
   modified TIMESTAMP NOT NULL
);

CREATE TABLE contact (
   contact_id INTEGER PRIMARY KEY,
   party_id INTEGER NOT NULL,
   address_id INTEGER NOT NULL,
   contact_preference VARCHAR(20) NOT NULL,
   modified TIMESTAMP NOT NULL,
   CONSTRAINT fk_contact_address FOREIGN KEY (address_id) REFERENCES address (address_id)
);

CREATE TABLE coverage (
   coverage_id INTEGER PRIMARY KEY,
   coverage_type_key VARCHAR(3) NOT NULL,
   transaction_id INTEGER NOT NULL,
   modified TIMESTAMP NOT NULL,
   CONSTRAINT fk_coverage_transaction FOREIGN KEY (transaction_id) REFERENCES transaction (transaction_id)
);

CREATE TABLE premium_detail (
   premium_detail_id INTEGER PRIMARY KEY,
   transaction_id INTEGER NOT NULL,
   base_annual_premium DECIMAL(8, 2),
   gst DECIMAL(2, 2),
   stamp_duty DECIMAL(2, 2),
   gross_annual_premium DECIMAL(8, 2),
   excess DECIMAL(6, 2),
   modified TIMESTAMP NOT NULL,
   CONSTRAINT fk_premium_detail_transaction FOREIGN KEY (transaction_id) REFERENCES transaction (transaction_id)
);

CREATE TABLE contents (
   contents_id INTEGER PRIMARY KEY,
   coverage_id INTEGER NOT NULL,
   sum_insured DECIMAL(10, 2),
   modified TIMESTAMP NOT NULL,
   CONSTRAINT fk_contents_coverage FOREIGN KEY (coverage_id) REFERENCES coverage (coverage_id)
);

CREATE TABLE occupancy (
   occupancy_id INTEGER PRIMARY KEY,
   occupancy_type_key VARCHAR(3) NOT NULL,
   rental_amount DECIMAL(7, 2),
   modified TIMESTAMP NOT NULL
);

CREATE TABLE property (
   property_id INTEGER PRIMARY KEY,
   coverage_id INTEGER NOT NULL,
   property_type_key VARCHAR(3) NOT NULL,
   roof_material_key VARCHAR(3) NOT NULL,
   wall_material_key VARCHAR(3) NOT NULL,
   occupancy_id INTEGER NOT NULL,
   year_of_construction INTEGER NOT NULL,
   sum_insured DECIMAL(12, 2),
   modified TIMESTAMP NOT NULL,
   CONSTRAINT fk_property_coverage FOREIGN KEY (coverage_id) REFERENCES coverage (coverage_id),
   CONSTRAINT fk_property_occupancy FOREIGN KEY (occupancy_id) REFERENCES occupancy (occupancy_id)
);
