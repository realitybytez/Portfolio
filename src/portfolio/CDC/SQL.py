sql = dict()

sql['get_table_metadata'] = """
SELECT 
table_name
, column_name
, data_type
, numeric_precision
, numeric_scale
FROM information_schema.columns
WHERE table_schema='public' AND table_catalog = 'policy_forge_read_replica'
order by table_name, ordinal_position
"""

sql['get_table_delta'] = """
SELECT *
FROM {0}
WHERE modified >= '{1}'
"""