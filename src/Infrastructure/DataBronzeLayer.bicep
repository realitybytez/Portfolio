var org = 'riskybizinsurance'
var env = 'dev'
var name = '${org}raw${env}'
var region = resourceGroup().location

// Specification
resource storageBronze 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: name
  location: region
  sku: {name: 'Standard_LRS'}
  kind: 'StorageV2'
  properties: {
      isHnsEnabled: true
      minimumTlsVersion: 'TLS1_2'  // Must be >= 1.2 end of Oct 2024
      publicNetworkAccess: 'Enabled' //todo as time allows - go private
    }  
  }

output id string = storageBronze.id
