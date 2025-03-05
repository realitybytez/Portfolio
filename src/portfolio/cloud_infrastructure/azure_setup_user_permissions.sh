#!/bin/bash
subscription_id="4327f6dd-2ade-4924-84a1-ce6e20d15662"
key_vault_name='portfolio3689'
os_user_secret_name='portfolioosuser'


az ad sp create-for-rbac --name appadmin --role Owner --scopes /subscriptions/$subscription_id > ~/Portfolio/src/portfolio/local_secrets/sp_app_admin.json
az logout

login_info="$HOME/Portfolio/src/portfolio/local_secrets/sp_app_admin.json"

appId=$(jq -r '.appId' "$login_info")
password=$(jq -r '.password' "$login_info")
tenant=$(jq -r '.tenant' "$login_info")

az login --service-principal --username "$appId" --password "$password" --tenant "$tenant"

az ad app create --display-name portfolio
porfolio_app_id=$(az ad app list --display-name portfolio --query "[].appId" -o tsv)
az ad sp create --id $porfolio_app_id

portfolio_login_info="$HOME/Portfolio/src/portfolio/local_secrets/sp_portfolio.json"
az role assignment create --assignee "$porfolio_app_id" --role "Key Vault Secrets User" --scope "/subscriptions/$subscription_id/resourceGroups/Portfolio/providers/Microsoft.KeyVault/vaults/$key_vault_name"
az ad sp credential reset --id $porfolio_app_id --query "{appId:appId, password:password, tenant:tenant}" -o json > $portfolio_login_info
az logout

portfolio_app_id=$(jq -r '.appId' "$portfolio_login_info")
portfolio_password=$(jq -r '.password' "$portfolio_login_info")
portfolio_tenant=$(jq -r '.tenant' "$portfolio_login_info")

az login --service-principal --username "$portfolio_app_id" --password "$portfolio_password" --tenant "$portfolio_tenant"
az keyvault secret show --name "$os_user_secret_name" --vault-name "$key_vault_name" --query value -o tsv > ~/Portfolio/src/portfolio/local_secrets/portfolio_os_user_secret.txt
az keyvault secret show --name "snowflake" --vault-name "$key_vault_name" --query value -o tsv > ~/Portfolio/src/portfolio/local_secrets/snowflake_secret.txt

#todo create os user for this work and chmod 600 password files to that user
chmod 600 $login_info
chmod 600 $portfolio_login_info
chmod 600 ~/Portfolio/src/portfolio/local_secrets/portfolio_os_user_secret.txt
chmod 600 ~/Portfolio/src/portfolio/local_secrets/snowflake_secret.txt

#todo setup automation to chmod +x shell scripts
#todo this is for while running locally only
chmod +x ./azure_deploy_infrastructure.sh
chmod +x ./python_venv_setup.sh
chmod +x ./postgres_setup.sh
chmod +x ~/Portfolio/src/portfolio/policy_forge_data_generator/policy_forge_write_data_to_replica.sh
chmod +x ~/Portfolio/src/portfolio/dagster_enable_server.sh
chmod +x ~/Portfolio/src/portfolio/dagster_enable_daemon.sh