DROP TABLE IF EXISTS source.policy CASCADE;
DROP TABLE IF EXISTS source.party CASCADE;
DROP TABLE IF EXISTS source.transaction CASCADE;
DROP TABLE IF EXISTS source.party_policy_association CASCADE;
DROP TABLE IF EXISTS source.address CASCADE;
DROP TABLE IF EXISTS source.contact CASCADE;
DROP TABLE IF EXISTS source.coverage CASCADE;
DROP TABLE IF EXISTS source.premium_detail CASCADE;
DROP TABLE IF EXISTS source.contents CASCADE;
DROP TABLE IF EXISTS source.occupancy CASCADE;
DROP TABLE IF EXISTS source.property CASCADE;
DROP TABLE IF EXISTS source.roof_material_type CASCADE;
DROP TABLE IF EXISTS source.property_occupation_type CASCADE;
DROP TABLE IF EXISTS source.property_type CASCADE;
DROP TABLE IF EXISTS source.address_type CASCADE;
DROP TABLE IF EXISTS source.transaction_status_type CASCADE;
DROP TABLE IF EXISTS source.transaction_type CASCADE;
DROP TABLE IF EXISTS source.coverage_type CASCADE;
DROP TABLE IF EXISTS source.wall_material_type CASCADE;

CREATE TABLE source.party (
   party_id INTEGER NOT NULL,
   given_name VARCHAR(50) NOT NULL,
   surname VARCHAR(50) NOT NULL,
   role VARCHAR(20) NOT NULL,
   modified TIMESTAMP NOT NULL,
   PRIMARY KEY (party_id, modified)
);

CREATE TABLE source.policy (
   policy_id INTEGER NOT NULL,
   policy_number VARCHAR(15) NOT NULL,
   channel VARCHAR(20) NOT NULL,
   inception TIMESTAMP NOT NULL,
   brand VARCHAR(30) NOT NULL,
   line_of_business VARCHAR(20) NOT NULL,
   modified TIMESTAMP NOT NULL,
   PRIMARY KEY (policy_id, modified)
);

CREATE TABLE source.party_policy_association (
   party_policy_id INTEGER NOT NULL,
   policy_id INTEGER NOT NULL,
   party_id INTEGER NOT NULL,
   modified TIMESTAMP NOT NULL,
   PRIMARY KEY (party_policy_id, modified)
);

CREATE TABLE source.transaction (
   transaction_id INTEGER NOT NULL,
   policy_id INTEGER NOT NULL,
   transaction_type_key VARCHAR(3) NOT NULL,
   transaction_state_key VARCHAR(3) NOT NULL,
   sequence int NOT NULL,
   effective TIMESTAMP NOT NULL,
   expiration TIMESTAMP NOT NULL,
   modified TIMESTAMP NOT NULL,
   PRIMARY KEY (transaction_id, modified)
);

CREATE TABLE source.address (
   address_id INTEGER NOT NULL,
   address_key VARCHAR(3) NOT NULL,
   address_line VARCHAR(100) NOT NULL,
   suburb VARCHAR(100) NOT NULL,
   postcode VARCHAR(4) NOT NULL,
   state VARCHAR(3) NOT NULL,
   country VARCHAR(2) NOT NULL,
   modified TIMESTAMP NOT NULL,
   PRIMARY KEY (address_id, modified)
);

CREATE TABLE source.contact (
   contact_id INTEGER NOT NULL,
   party_id INTEGER NOT NULL,
   address_id INTEGER NOT NULL,
   contact_preference VARCHAR(20) NOT NULL,
   modified TIMESTAMP NOT NULL,
   PRIMARY KEY (contact_id, modified)
);

CREATE TABLE source.coverage (
   coverage_id INTEGER NOT NULL,
   coverage_type_key VARCHAR(3) NOT NULL,
   transaction_id INTEGER NOT NULL,
   modified TIMESTAMP NOT NULL,
   PRIMARY KEY (coverage_id, modified)
);

CREATE TABLE source.premium_detail (
   premium_detail_id INTEGER NOT NULL,
   transaction_id INTEGER NOT NULL,
   base_annual_premium DECIMAL(8, 2),
   gst DECIMAL(2, 2),
   stamp_duty DECIMAL(2, 2),
   gross_annual_premium DECIMAL(8, 2),
   excess DECIMAL(6, 2),
   modified TIMESTAMP NOT NULL,
   PRIMARY KEY (premium_detail_id, modified)
);

CREATE TABLE source.contents (
   contents_id INTEGER NOT NULL,
   coverage_id INTEGER NOT NULL,
   sum_insured DECIMAL(10, 2),
   modified TIMESTAMP NOT NULL,
   PRIMARY KEY (contents_id, modified)
);

CREATE TABLE source.occupancy (
   occupancy_id INTEGER NOT NULL,
   occupancy_type_key VARCHAR(3) NOT NULL,
   rental_amount DECIMAL(7, 2),
   modified TIMESTAMP NOT NULL,
   PRIMARY KEY (occupancy_id, modified)
);

CREATE TABLE source.property (
   property_id INTEGER NOT NULL,
   coverage_id INTEGER NOT NULL,
   property_type_key VARCHAR(3) NOT NULL,
   roof_material_key VARCHAR(3) NOT NULL,
   wall_material_key VARCHAR(3) NOT NULL,
   occupancy_id INTEGER NOT NULL,
   year_of_construction INTEGER NOT NULL,
   sum_insured DECIMAL(12, 2),
   modified TIMESTAMP NOT NULL,
   PRIMARY KEY (property_id, modified)
);

CREATE TABLE source.roof_material_type (
    type_id INTEGER NOT NULL,
    type_key VARCHAR(3) NOT NULL,
    type_desc VARCHAR(50) NOT NULL,
    modified TIMESTAMP NOT NULL
);

CREATE TABLE source.property_occupation_type (
    type_id INTEGER NOT NULL,
    type_key VARCHAR(3) NOT NULL,
    type_desc VARCHAR(50) NOT NULL,
    modified TIMESTAMP NOT NULL
);

CREATE TABLE source.property_type (
    type_id INTEGER NOT NULL,
    type_key VARCHAR(3) NOT NULL,
    type_desc VARCHAR(50) NOT NULL,
    modified TIMESTAMP NOT NULL
);

CREATE TABLE source.address_type (
    type_id INTEGER NOT NULL,
    type_key VARCHAR(3) NOT NULL,
    type_desc VARCHAR(50) NOT NULL,
    modified TIMESTAMP NOT NULL
);

CREATE TABLE source.transaction_status_type (
    type_id INTEGER NOT NULL,
    type_key VARCHAR(3) NOT NULL,
    type_desc VARCHAR(50) NOT NULL,
    modified TIMESTAMP NOT NULL
);

CREATE TABLE source.transaction_type (
    type_id INTEGER NOT NULL,
    type_key VARCHAR(3) NOT NULL,
    type_desc VARCHAR(50) NOT NULL,
    modified TIMESTAMP NOT NULL
);

CREATE TABLE source.coverage_type (
    type_id INTEGER NOT NULL,
    type_key VARCHAR(3) NOT NULL,
    type_desc VARCHAR(50) NOT NULL,
    modified TIMESTAMP NOT NULL
);

CREATE TABLE source.wall_material_type (
    type_id INTEGER NOT NULL,
    type_key VARCHAR(3) NOT NULL,
    type_desc VARCHAR(50) NOT NULL,
    modified TIMESTAMP NOT NULL
);