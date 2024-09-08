// What should be common
// Too bad names can't be computed from outputs from another module...
var org = 'riskybizinsurance'
var env = 'dev'

//RG Specific
var region = resourceGroup().location

// VM Resource
var app = 'policyforge'
var vm_resource_name = app
var vm_admin_user = '${app}admin'
param vm_ssh_key string
var vm_image = {
    publisher: 'Canonical'
    offer: '0001-com-ubuntu-server-jammy'
    sku: '22_04-lts-gen2'
    version: 'latest'
  }
var vm_size = 'Standard_B2ats_v2'
var vm_disk_type = 'Standard_LRS'

// OS conf /w auth
var os_config = {
  disablePasswordAuthentication: true
  ssh: {
    publicKeys: [
      {
        path: '/home/${vm_admin_user}/.ssh/authorized_keys'
        keyData: vm_ssh_key
      }
    ]
  }
}

// Virtual Network
var virtual_network_name = '${org}${env}virtualnetwork'
var address_prefix = '10.1.0.0/16'
var subnet_name = '${app}${env}subnet'
var subnet_address_prefix = '10.1.0.0/24'

// NSG
var network_security_group_name = '${app}${env}networksecuritygroup'

//NIC
var network_interface_name = '${app}${env}networkinterface'

//Public IP
var public_ip_address_name = '${app}${env}publicip'

//DNS
var dns_name = '${app}${env}dns'


// Specification
resource networkInterface 'Microsoft.Network/networkInterfaces@2024-01-01' = {
  name: network_interface_name
  location: region
  properties: {
    ipConfigurations: [
      {
        name: '${app}${env}ipconfig'
        properties: {
          subnet: {
            id: virtualNetwork.properties.subnets[0].id
          }
          privateIPAllocationMethod: 'Dynamic'
          publicIPAddress: {
            id: publicIPAddress.id
          }
        }
      }
    ]
    networkSecurityGroup: {
      id: networkSecurityGroup.id
    }
  }
}

resource networkSecurityGroup 'Microsoft.Network/networkSecurityGroups@2024-01-01' = {
  name: network_security_group_name
  location: region
  properties: {
    securityRules: [
      {
        name: 'SSH'
        properties: {
          priority: 1000
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '22'
        }
      }
    ]
  }
}

resource virtualNetwork 'Microsoft.Network/virtualNetworks@2024-01-01' = {
  name: virtual_network_name
  location: region
  properties: {
    addressSpace: {
      addressPrefixes: [
        address_prefix
      ]
    }
    subnets: [
      {
        name: subnet_name
        properties: {
          addressPrefix: subnet_address_prefix
          privateEndpointNetworkPolicies: 'Enabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
        }
      }
    ]
  }
}

resource publicIPAddress 'Microsoft.Network/publicIPAddresses@2024-01-01' = {
  name: public_ip_address_name
  location: region
  sku: {
    name: 'Basic'
  }
  properties: {
    publicIPAllocationMethod: 'Dynamic'
    publicIPAddressVersion: 'IPv4'
    dnsSettings: {
      domainNameLabel: dns_name
    }
    idleTimeoutInMinutes: 4
  }
}

resource vm 'Microsoft.Compute/virtualMachines@2023-09-01' = {
  name: vm_resource_name
  location: region
  properties: {
    hardwareProfile: {
      vmSize: vm_size
    }

    storageProfile: {
      osDisk: {
        createOption: 'FromImage'
        managedDisk: {
          storageAccountType: vm_disk_type
        }
      }
      imageReference: vm_image
    }

    networkProfile: {
      networkInterfaces: [
        {
          id: networkInterface.id
        }
      ]
    }

    osProfile: {
      computerName: vm_resource_name
      adminUsername: vm_admin_user
      adminPassword: vm_ssh_key
      linuxConfiguration: os_config
    }
  }
}

output adminUsername string = vm_admin_user
output hostname string = publicIPAddress.properties.dnsSettings.fqdn
output sshCommand string = 'ssh ${vm_admin_user}@${publicIPAddress.properties.dnsSettings.fqdn}'
