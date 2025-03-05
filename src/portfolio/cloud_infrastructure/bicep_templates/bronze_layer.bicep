var org = 'rbi'
var env = 'prod'
var name = '${org}${env}${uniqueString(resourceGroup().id)}'
var location = resourceGroup().location
var container_name = 'bronze'

// Specification
resource storageBronze 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: name
  location: location
  sku: {name: 'Standard_LRS'}
  kind: 'StorageV2'
  properties: {
      isHnsEnabled: true
      minimumTlsVersion: 'TLS1_2'  // Must be >= 1.2 end of Oct 2024
      publicNetworkAccess: 'Enabled' //todo as time allows - go private
    }  
  }

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  name: 'default'
  parent: storageBronze
}

resource BronzeContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: container_name
  parent: blobService
  properties: {
    publicAccess: 'None'
  }
}

output id string = storageBronze.id
