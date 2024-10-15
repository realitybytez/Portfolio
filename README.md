# Portfolio

1. Setup Cloud Services
```
# Create a fresh Azure subscription / use existing subscription
# Create a fresh Snowflake account / use existing account
```

2. Define Secrets
```
# Create an Azure Key Vault utilising RBAC
Give yourself the following roles:
Key Vault Administrator
Key Vault Secrets Officer

# Create a stecret storing the password used for snowflake
Name: snowflake
Secret value: <choose a password>

# Create a secret storing the password to be used for an OS user on an Azure VM
Name: portfolioosuser
Secret value: <choose a password>

```

3. Clone this repo in ~ (e.g. $HOME) on a linux box
```
git clone git@github.com:realitybytez/Portfolio.git
```

4. Install dependencies
``` 
sudo apt-get install jq
wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/bin/yq
chmod +x /usr/bin/yq
```

5. Configure variables
```
# Update the following variables in script below
# subscription_id: Azure subscription ID 
# key_vault_name: Name of key vault created above

~/Portfolio/src/portfolio/Infrastructure/SetupUsersPermissions.sh

snowflake:
  account: abnyhbb-fm74053 # Populated by user
  user: realitybytez # Populated by the user
```

6. Run Azure setup scripts
```
# Log in to Azure CLI as the owner
az login
# Run SetupUsersPermissions.sh (Infrastructure)
# Run DeployInfrastructure.sh (Infrastructure)
```

7. Enable Snowflake Integration
```
Run setup_snowflake.py (Infrastructure)
DESC INTEGRATION portfolio_bronze_layer;
# Take the value in AZURE_CONSENT_URL, open it in a browser and accept the prompt
# Note the value in AZURE_MULTI_TENANT_APP_NAME e.g cfbkjasnowflakepacint_1727079109755
# Take the name e.g cfbkjasnowflakepacint and give it the storage blob data reader role on
# the storage container blob store created by point 6
```

8. If components testing locally
```
# Run build_environment.sh (Infrastructure)
# Run setup_postgres.sh (Infrastructure)
