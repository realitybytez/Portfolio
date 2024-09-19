sql = dict()

sql['get_table_metadata'] = """
SELECT 
table_name
, column_name
, data_type
, numeric_precision
, numeric_scale
FROM information_schema.columns
WHERE table_schema='source' AND table_catalog = 'policy_forge_replica'
order by table_name, ordinal_position
"""

sql['get_table_delta'] = """
SELECT *
FROM source.{0}
WHERE modified > '{1}'
"""

sql['get_last_modified'] = """
SELECT max(modified)
FROM source.{0}
WHERE modified > '{1}'
"""