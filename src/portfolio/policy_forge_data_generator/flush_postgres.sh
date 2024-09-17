#!/bin/sh

os_password="$HOME/Portfolio/src/portfolio/local_secrets/portfolio_os_user_secret.txt"
password=$(cat $os_password)
host='localhost'
port='5432'
db_name='policy_forge_replica'
db_user='policy_forge_user'
db_schema='source'
code_dir="${HOME}/Portfolio/src/portfolio/policy_forge_data_generator"
create_schema_script="PolicyForgeDDL.sql"

psql -h "$host" -p "$port" -U "$db_user" -d "$db_name" -c "drop schema source cascade;"
sudo -S -u postgres psql -U postgres -d $db_name -c "CREATE SCHEMA $db_schema AUTHORIZATION $db_user;" <$os_password
cd $code_dir
psql -h "$host" -p "$port" -U "$db_user" -d "$db_name" -f "$create_schema_script"

#psql -h localhost -p 5432 -U policy_forge_user -d policy_forge_replica