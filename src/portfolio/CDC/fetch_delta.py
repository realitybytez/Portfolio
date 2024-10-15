from psycopg2 import connect
from azure.storage.blob import ContainerClient
import yaml
from SQL import sql
from datetime import datetime
import pyarrow
import pyarrow.parquet as parquet
import os
import os.path as path
import pickle
import json
import snowflake.connector

base_path = os.path.join(os.path.expanduser("~"), 'Portfolio/src/portfolio/CDC')
parent_path = os.path.join(os.path.expanduser("~"), 'Portfolio/src/portfolio')
secrets_folder = path.join(parent_path, 'local_secrets')
storage_creds = 'storage_account_credentials.json'

def get_job_state(metadata):

    if os.path.exists(path.join(base_path, 'job_state.pkl')):
        with open(path.join(base_path, 'job_state.pkl'), 'rb') as f:
            state = pickle.load(f)
    else:
        # Just needs to be any time before policy forge go live, how about unix epoch
        table_names = [m[0] for m in metadata]
        state = dict()
        for t in table_names:
            state[t] = {'last_modified_datetime': datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0)}
    return state

def set_job_state(state):
    with open(path.join(base_path, 'job_state.pkl'), 'wb') as file:
        pickle.dump(state, file)

def get_secret(cfg):
    with open(cfg['secret_store']) as f:
        secret = f.readline().strip()
    return secret

def get_cfg():
    with open(f'{parent_path}/Infrastructure/config.yml', 'r') as file:
        cfg = yaml.safe_load(file)
    return cfg

def get_storage_account_credential():
    with open(path.join(secrets_folder, storage_creds), 'r') as f:
        _json = json.load(f)
        return _json[-1]['value']


def get_delta():
    infra_cfg = get_cfg()
    cfg = infra_cfg['postgres']

    db_pyarrow_mapping = {
        'character varying': pyarrow.string(),
        'integer': pyarrow.int32(),
        'timestamp without time zone': pyarrow.timestamp('s', tz='Australia/Sydney'),
        'numeric': pyarrow.decimal128(12, 2)
    }

    conn = connect(user=cfg['user'], password=get_secret(cfg), host=cfg['host'], port=cfg['port'], database=cfg['database'])

    cursor = conn.cursor()
    cursor.execute(sql['get_table_metadata'])
    metadata = cursor.fetchall()

    schemas = dict()
    seen_tables = set()
    for result in metadata:
        if result[0] not in seen_tables:
            schemas[result[0]] = []
            seen_tables.add(result[0])
        schemas[result[0]].append((result[1], db_pyarrow_mapping[result[2]]))

    state = get_job_state(metadata)
    storage_account_name = infra_cfg['storage_account_name']

    container_client = ContainerClient(account_url=f"https://{storage_account_name}.blob.core.windows.net/",
                                       credential=get_storage_account_credential(),
                                       container_name='bronze')

    with open(os.path.join(parent_path, infra_cfg['snowflake']['secret_store']), 'r') as file:
        os.environ['SNOWFLAKE_PASSWORD'] = file.readline().strip()

    sf_conn = snowflake.connector.connect(
        user=infra_cfg['snowflake']['user'],
        password=os.environ['SNOWFLAKE_PASSWORD'],
        account=infra_cfg['snowflake']['account']
    )

    sf_cursor = sf_conn.cursor()

    for schema_name, schema_data in schemas.items():
        print('Last modified is for', schema_name, 'is', state[schema_name]['last_modified_datetime'])
        query = sql['get_table_delta'].format(schema_name, state[schema_name]['last_modified_datetime'])
        cursor.execute(query)
        table = cursor.fetchall()
        if len(table) == 0:
            continue
        schema = pyarrow.schema(schema_data)
        columns = list(zip(*table))

        dict_arrays = dict()
        for i, data in enumerate(schema_data):
            dict_arrays[data[0]] = columns[i]

        table = pyarrow.Table.from_pydict(dict_arrays, schema)

        query = sql['get_last_modified'].format(schema_name, state[schema_name]['last_modified_datetime'])
        cursor.execute(query)
        result = cursor.fetchall()
        state[schema_name]['last_modified_datetime'] = result[0][0]
        print('Last modified is now', state[schema_name]['last_modified_datetime'])

        # todo temp solution until on cloud WH infra
        if not os.path.exists(f'{parent_path}/bronze/sources/policy_forge/{schema_name}'):
            os.makedirs(f'{parent_path}/bronze/sources/policy_forge/{schema_name}')

        last_mod = result[0][0].strftime("%Y-%m-%d-%H-%M-%S")

        fp = f'{parent_path}/bronze/sources/policy_forge/{schema_name}/{last_mod}.parquet'
        blob_fp = f'sources/policy_forge{schema_name}/{last_mod}.parquet'
        parquet.write_table(table, fp)

        with open(fp, 'rb') as up:
            container_client.upload_blob(name=blob_fp, data=up)

        sf_cursor.execute(f'ALTER EXTERNAL TABLE BRONZE_PROD.RAW.{schema_name} REFRESH;')

    set_job_state(state)
