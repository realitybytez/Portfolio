import snowflake_lakehouse as lakehouse
import yaml
import os
import snowflake.connector
from psycopg2 import connect
from itertools import groupby

base_path = os.path.join(os.path.expanduser("~"), 'Portfolio/src/portfolio/cloud_infrastructure')
parent_path = os.path.join(os.path.expanduser("~"), 'Portfolio/src/portfolio')

with open(f'{base_path}/shared_config.yml', 'r') as file:
    cfg = yaml.safe_load(file)

sf_cfg = cfg['snowflake']

with open (os.path.join(parent_path, sf_cfg['secret_store']), 'r') as file:
    os.environ['SNOWFLAKE_PASSWORD'] = file.readline().strip()

pg_cfg = cfg['postgres']

with open (os.path.join(parent_path, pg_cfg['secret_store']), 'r') as file:
    os.environ['PG_PASS'] = file.readline().strip()

pg_conn = connect(user=pg_cfg['user'], password=os.environ['PG_PASS'], host=pg_cfg['host'], port=pg_cfg['port'], database=pg_cfg['database'])

pg_query = """
SELECT 
table_name
, column_name
, data_type
, character_maximum_length
, numeric_precision
, numeric_scale
FROM information_schema.columns
WHERE table_schema='source' AND table_catalog = 'policy_forge_replica'
order by table_name, ordinal_position
"""

pg_cursor = pg_conn.cursor()
pg_cursor.execute(pg_query)
metadata = pg_cursor.fetchall()
metadata = [x for x in metadata]

tables = dict()
for key, group in groupby(metadata, key=lambda x:x[0]):
    tables[key] = dict()
    for x in group:
        tables[key][x[1]] = x[2:]


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

print('Building bronze layer data structures...')
for table_name, table_data in tables.items():
    print(f'processing {table_name}')
    field_spec = ''
    for column_name, column_data in table_data.items():
        _type = pg_to_sf_type_map[column_data[0]]
        if _type == 'varchar':
            _type_data = f'{_type}({column_data[1]})'
        elif _type == 'number':
            _type_data = f'{_type}({column_data[2]}, {column_data[3]})'
        else:
            _type_data = _type
        field_spec += f'\n,{column_name} {_type_data} AS (value:{column_name}::{_type_data})'

    fully_qualified_table_name = f'BRONZE_PROD.RAW.{table_name}'
    sf_cursor.execute(lakehouse.sql['generate_stage'].format(fully_qualified_table_name, cfg['storage_account_name'], 'policy_forge', table_name))
    sf_cursor.execute(lakehouse.sql['generate_external_table'].format(fully_qualified_table_name, field_spec, fully_qualified_table_name))

pg_conn.close()
sf_conn.close()

