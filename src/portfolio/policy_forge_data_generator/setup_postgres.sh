#chmod +x
os_password="$HOME/Portfolio/src/portfolio/local_secrets/portfolio_os_user_secret.txt"
password=$(cat $os_password)
postgresuser='postgres'
host='localhost'
port='5432'
db_name='policy_forge_replica'
db_schema='source'
db_user='policy_forge_user'
db_password=$os_password
pg_pass_file="${HOME}/.pgpass"
code_dir="${HOME}/Portfolio/src/portfolio/policy_forge_data_generator"
create_schema_script="PolicyForgeDDL.sql"

# Install Postgres and make sure it's running
cd ~
sudo -S apt install -y postgresql <$os_password
sudo -S apt install -y postgresql-client <$os_password
sudo -S systemctl start postgresql <$os_password
sudo -S systemctl enable postgresql <$os_password

cd /tmp  # postgres user won't have access to user's home, go anywhere but there to prevent errors

# Setup minimal database environment & access
sudo -S -u postgres psql -U postgres -c "CREATE DATABASE $db_name;" <$os_password
sudo -S -u postgres psql -U postgres -c "CREATE USER $db_user PASSWORD '$password';" <$os_password
sudo -S -u postgres psql -U postgres -d $db_name -c "CREATE SCHEMA $db_schema AUTHORIZATION $db_user;" <$os_password

# Setup .pg_pass file
cd ~
touch "$pg_pass_file"
chmod 600 "$pg_pass_file"
echo "$host:$port:$db_name:$db_user:$password" > $pg_pass_file

# Create schema in DB
cd $code_dir
psql -h "$host" -p "$port" -U "$db_user" -d "$db_name" -f "$create_schema_script"


