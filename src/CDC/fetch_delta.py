from psycopg2 import connect
import yaml
from secret import secret
from SQL import sql
from datetime import datetime
import pyarrow
import pyarrow.parquet as parquet

with open('config.yml', 'r') as file:
    cfg = yaml.safe_load(file)['db_params']

db_pyarrow_mapping = {
    'character varying': pyarrow.string(),
    'integer': pyarrow.int32(),
    'timestamp without time zone': pyarrow.timestamp('s'),
    'numeric': pyarrow.decimal128(12, 2)
}

conn = connect(user=cfg['user'], password=secret['postgres_password'], host=cfg['host'], port=cfg['port'], database=cfg['database'])

# todo temp solution until on cloud WH infra
last_query_time = datetime(year=2006, month=3, day=25, hour=0, minute=0, second=0)

cursor = conn.cursor()
cursor.execute(sql['get_table_metadata'])
results = cursor.fetchall()

table_names = {x[0] for x in results}
schemas = dict()
seen_tables = set()
for result in results:
    if result[0] not in seen_tables:
        schemas[result[0]] = []
        seen_tables.add(result[0])
    schemas[result[0]].append((result[1], db_pyarrow_mapping[result[2]]))

for schema_name, schema_data in schemas.items():
    query = sql['get_table_delta'].format(schema_name, last_query_time)
    cursor.execute(query)
    table = cursor.fetchall()
    schema = pyarrow.schema(schema_data)
    columns = list(zip(*table))

    dict_arrays = dict()
    for i, data in enumerate(schema_data):
        dict_arrays[data[0]] = columns[i]

    table = pyarrow.Table.from_pydict(dict_arrays, schema)

    # todo temp solution until on cloud WH infra
    parquet.write_table(table, f'{schema_name}.parquet')


