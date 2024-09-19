from psycopg2 import connect
import yaml
from SQL import sql
from datetime import datetime
import pyarrow
import pyarrow.parquet as parquet
import os
import os.path as path
import pickle

base_path = os.path.join(os.path.expanduser("~"), 'Portfolio/src/portfolio/CDC')
parent_path = os.path.join(os.path.expanduser("~"), 'Portfolio/src')
run_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

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
    with open(path.join(parent_path, cfg['secret_store'])) as f:
        secret = f.readline().strip()
    return secret

def get_cfg():
    with open(f'{base_path}/config.yml', 'r') as file:
        cfg = yaml.safe_load(file)['db_params']
    return cfg

def get_delta():
    cfg = get_cfg()

    db_pyarrow_mapping = {
        'character varying': pyarrow.string(),
        'integer': pyarrow.int32(),
        'timestamp without time zone': pyarrow.timestamp('s'),
        'numeric': pyarrow.decimal128(12, 2)
    }

    if not os.path.exists(f'{parent_path}/bronze/sources/policy_forge/{run_time}'):
        os.makedirs(f'{parent_path}/bronze/sources/policy_forge/{run_time}')
    print('make', f'{parent_path}/bronze/sources/policy_forge/{run_time}')

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
        print('state for', schema_name, 'is now', result[0][0])

        # todo temp solution until on cloud WH infra

        parquet.write_table(table, f'{parent_path}/bronze/sources/policy_forge/{run_time}/{schema_name}.parquet')
        print('write', f'{parent_path}/bronze/sources/policy_forge/{run_time}/{schema_name}.parquet')
    set_job_state(state)
