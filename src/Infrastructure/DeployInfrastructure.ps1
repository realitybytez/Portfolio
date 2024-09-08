$tenant = '4709ea8c-d3bd-4226-9769-cd360ea2e962'
$resource_group = "Portfolio"
$location = "australiaeast"
$app_server_spec = 'C:\Users\User\Desktop\Portfolio\src\Infrastructure\AppServer.bicep'
$ssh_public_key = Get-Content "C:\Users\User\.ssh\portfolio.pub" -raw

az login --tenant $tenant
az group create --name $resource_group --location $location
az deployment group create --resource-group $resource_group --template-file $app_server_spec --parameters vm_ssh_key=$ssh_public_key
