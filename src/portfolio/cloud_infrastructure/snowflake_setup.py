import snowflake_lakehouse as lakehouse
import yaml
import os
import snowflake.connector

base_path = os.path.join(os.path.expanduser("~"), 'Portfolio/src/portfolio/cloud_infrastructure')
parent_path = os.path.join(os.path.expanduser("~"), 'Portfolio/src/portfolio')

with open(f'{base_path}/shared_config.yml', 'r') as file:
    cfg = yaml.safe_load(file)

sf_cfg = cfg['snowflake']

with open (os.path.join(parent_path, sf_cfg['secret_store']), 'r') as file:
    os.environ['SNOWFLAKE_PASSWORD'] = file.readline().strip()

sf_conn = snowflake.connector.connect(
    user=cfg['snowflake']['user'],
    password=os.environ['SNOWFLAKE_PASSWORD'],
    account=cfg['snowflake']['account']
)

sf_cursor = sf_conn.cursor()

pg_to_sf_type_map = {
    'timestamp without time zone': 'timestamp_ntz',
    'character varying': 'varchar',
    'integer': 'integer',
    'numeric': 'number'
}

print('Building Snowflake warehouse structure...')
sf_cursor.execute(lakehouse.sql['build_warehouse_structure'], num_statements=13)
print('Configuring Azure integration...')
sf_cursor.execute(lakehouse.sql['setup_azure_integration'].format(cfg['tenant'], cfg['storage_account_name']))
print('Granting roles...')
sf_cursor.execute(lakehouse.sql['grant_roles'])
sf_conn.close()
print('Complete!')