sql = dict()

sql['build_warehouse_structure'] = """
CREATE WAREHOUSE PORTFOLIO;
CREATE DATABASE BRONZE_DEV;
CREATE DATABASE BRONZE_PROD;
CREATE SCHEMA BRONZE_DEV.RAW;
CREATE SCHEMA BRONZE_PROD.RAW;
CREATE DATABASE SILVER_DEV;
CREATE DATABASE SILVER_PROD;
CREATE SCHEMA SILVER_DEV.CLEAN;
CREATE SCHEMA SILVER_PROD.CLEAN;
CREATE DATABASE GOLD_DEV;
CREATE DATABASE GOLD_PROD;
CREATE SCHEMA GOLD_DEV.BUSINESS_UNIT_DATAMART;
CREATE SCHEMA GOLD_PROD.BUSINESS_UNIT_DATAMART;
"""

sql['setup_azure_integration'] = """
CREATE STORAGE INTEGRATION portfolio_bronze_layer
TYPE = EXTERNAL_STAGE
STORAGE_PROVIDER = 'AZURE'
ENABLED = TRUE
AZURE_TENANT_ID = '{0}'
STORAGE_ALLOWED_LOCATIONS = ('azure://{1}.blob.core.windows.net/bronze/');
"""

sql['grant_roles'] = """
GRANT USAGE ON INTEGRATION portfolio_bronze_layer TO ROLE ACCOUNTADMIN;
"""

sql['generate_stage'] = """
CREATE OR REPLACE STAGE {0}
STORAGE_INTEGRATION = portfolio_bronze_layer
URL = 'azure://{1}.blob.core.windows.net/bronze/sources/{2}/{3}/';
"""

sql['generate_external_table'] = """
CREATE EXTERNAL TABLE {0} (
  date_part date AS TO_DATE (
    SPLIT_PART(SPLIT_PART(metadata$filename, '/', 4), '-', 1) || '/' ||
    SPLIT_PART(SPLIT_PART(metadata$filename, '/', 4), '-', 2) || '/' ||
    SPLIT_PART(SPLIT_PART(metadata$filename, '/', 4), '-', 3),
    'YYYY/MM/DD'
  )
  {1}
  ,cdc_snapshot TIMESTAMP_NTZ AS TO_TIMESTAMP_NTZ(SPLIT_PART(SPLIT_PART(metadata$filename, '/', 4), '.', 1), 'YYYY-MM-DD-HH24-MI-SS') 

)
  PARTITION BY (date_part)
  LOCATION=@{2}/
  AUTO_REFRESH = true
  FILE_FORMAT = (TYPE = PARQUET);
"""
