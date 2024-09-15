# Portfolio

1. Clone this repo in ~ (e.g. $HOME) on a linux box
```commandline
git clone git@github.com:realitybytez/Portfolio.git
```
2. Install dependencies
```commandline 
sudo apt-get install jq
```

3. Run one time setup for an Azure instance
```
# Create a fresh Azure subscription
# Create an Azure Key Vault utilising RBAC in your subscription
Give yourself the following roles:
Key Vault Administrator
Key Vault Secrets Officer

# Create a secret storing the password to be used for an OS user on an Azure VM
Name: portfolioosuser
Secret value: <choose a password>

# Log in to Azure CLI as the owner
# Update the following variables in script below
# subscription_id: Azure subscription ID 
# key_vault_name: Name of key vault created above

~/Portfolio/src/portfolio/Infrastructure/SetupUsersPermissions.sh

# Run the script... todo eventually this will be master that kicks off all infra not just immediate users & permissions

# temp
# Run build_environment.sh (Infrastructure)
# Run setup_postgres.sh (policy_forge_data_generator)
```
