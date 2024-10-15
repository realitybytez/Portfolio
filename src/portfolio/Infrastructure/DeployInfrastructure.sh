tenant='4709ea8c-d3bd-4226-9769-cd360ea2e962'
resource_group="Portfolio"
location="australiaeast"
#ssh_public_key = Get-Content "C:\Users\User\.ssh\portfolio.pub" -raw
app_server_spec='C:\Users\User\Desktop\Portfolio\src\Infrastructure\AppServer.bicep'
bronze_layer_spec='./DataBronzeLayer.bicep'
storage_account_credentials="$HOME/Portfolio/src/portfolio/local_secrets/storage_account_credentials.json"
cdc_config="$HOME/Portfolio/src/portfolio/CDC/config.yml"
infra_config="$HOME/Portfolio/src/portfolio/Infrastructure/config.yml"


az login --tenant $tenant
az group create --name $resource_group --location $location
az deployment group create --resource-group $resource_group --template-file $app_server_spec --parameters vm_ssh_key=$ssh_public_key
response=$(az deployment group create --resource-group $resource_group --template-file $bronze_layer_spec --output json)
storage_account_name=$(echo "$response" | jq -r '.properties.dependencies[0].dependsOn[0].resourceName')
yq -i ".storage_account_name = \"$storage_account_name\"" "$infra_config"
yq -i ".tenant = \"$tenant\"" "$infra_config"
az storage account keys list -g Portfolio -n $storage_account_name > $storage_account_credentials
chmod 600 $storage_account_credentials

#todo rewrite fully for sh and integrate into setup user permissions.