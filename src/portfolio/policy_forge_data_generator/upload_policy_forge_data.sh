host='localhost'
port='5432'
db_name='policy_forge_replica'
db_user='policy_forge_user'
upload_data_script=$1

psql -h "$host" -p "$port" -U "$db_user" -d "$db_name" -f "$upload_data_script"