#chmod +x
postgresuser='postgres'
host='localhost'
port='5432'
db_name='policy_forge_replica'
db_user='policy_forge_user'
db_password=$(cat ./password.txt)
pg_pass_file="${HOME}/.pgpass"
code_dir="~" # todo update for cloud release
create_schema_script="PolicyForgeDDL.sql"

# Install Postgres and make sure it's running
cd ~
# Not most secure way to store a password... to be updated later.
sudo -S apt install -y postgresql <~/password.txt
sudo apt install -y postgresql-client <~/password.txt
sudo -S systemctl start postgresql <~/password.txt
sudo -S systemctl enable postgresql <~/password.txt

cd /tmp  # postgres user won't have access to user's home, go anywhere but there to prevent errors

# Setup minimal database environment & access
sudo -S -u postgres psql -U postgres -c "CREATE DATABASE $db_name;" <~/password.txt
sudo -S -u postgres psql -U postgres -c "CREATE USER $db_user PASSWORD '$db_password';" <~/password.txt
sudo -S -u postgres psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $db_name TO replica_uploader;" <~/password.txt

# Setup .pg_pass file
cd ~
touch "$pg_pass_file"
chmod 600 $pg_pass_file
echo "$host:$port:$db_name:$db_user:$db_password" > $pg_pass_file

# Create schema in DB
cd $code_dir
psql -h "$host" -p "$port" -U "$db_user" -d "$db_name" -f "$create_schema_script"


