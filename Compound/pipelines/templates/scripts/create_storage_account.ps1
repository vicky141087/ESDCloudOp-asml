param
(
    [Parameter(Mandatory=$true)]
    [string] $subnetId,
    [Parameter(Mandatory=$true)]
    [string] $subscriptionId,
    [Parameter(Mandatory=$true)]
    [string] $resourceGroup,
    [Parameter(Mandatory=$true)]
    [string] $storageAccountName,
    [string] $location = "westeurope",
    [string] $containerName = "tfstate",
    [Parameter(Mandatory=$true)]
    [string] $privateDnsSubscriptionId,
    [Parameter(Mandatory=$true)]
    [string] $privateDnsResourceGroupName,
    [Parameter(Mandatory=$true)]
    [string[]] $principleIds
)

function Invoke-AzCommand {
    [CmdletBinding()]
    param(
        [scriptblock] $ScriptBlock = {}
    )
 
    Invoke-Command -ScriptBlock $scriptBlock
    if ($LASTEXITCODE) { 
       throw "ERROR" 
    }
 }
 
function New-TerraformStateStorageAccount {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string] $subnetId,
        [Parameter(Mandatory=$true)]
        [string] $subscriptionId,
        [Parameter(Mandatory=$true)]
        [string] $resourceGroup,
        [Parameter(Mandatory=$true)]
        [string] $storageAccountName,
        [string] $location = "westeurope",
        [string] $containerName = "tfstate",
        [Parameter(Mandatory=$true)]
        [string] $privateDnsSubscriptionId,
        [Parameter(Mandatory=$true)]
        [string] $privateDnsResourceGroupName,
        [Parameter(Mandatory=$true)]
        [string[]] $principleIds
    )

    $sa_private_enpoint_name ="$storageAccountName-pep"

    $rg = New-ResourceGroup `
        -subscriptionId $subscriptionId `
        -resourceGroup $resourceGroup `
        -location $location `

    $sa = New-StorageAccount `
        -subscriptionId $subscriptionId `
        -resourceGroup $resourceGroup `
        -storageAccountName $storageAccountName `
        -location $location

    New-PrivateEndpoint `
        -sa_private_enpoint_name $sa_private_enpoint_name `
        -resourceGroup $resourceGroup `
        -subnetId $subnetId `
        -storageAccountId $sa.id `
    | Out-Null
    
    Get-StoragePrivateEndpointId `
        -name $sa_private_enpoint_name `
        -resourceGroup $resourceGroup `
    | Out-Null

    $network_interface_id = Get-NetworkInterfaceId `
        -name $sa_private_enpoint_name `
        -resourceGroup $resourceGroup 

    $storage_network_interface_private_ip = Get-NetworkIntefacePrivateIp -networkInterfaceId $network_interface_id


    New-DnsRecord `
        -storageAccountName $storageAccountName `
        -privateDnsResourceGroupName $privateDnsResourceGroupName `
        -privateDnsSubscriptionId $privateDnsSubscriptionId `
        -storageAccountPrivateEndpointName $sa_private_enpoint_name `
        -storageAccountPrivateIp $storage_network_interface_private_ip `
    | Out-Null

    New-StorageContainer `
        -containerName $containerName `
        -storageAccountName $storageAccountName `
        -subscriptionId $subscriptionId `
        -resourceGroup $resourceGroup `
    | Out-Null

    $storage_private="$storageAccountName.privatelink.blob.core.windows.net"
    # Write-Verbose $storage_private

    $ReaderAndDataAccess = "c12c1c16-33a1-487b-954d-41c89c60f349"
    New-RoleAssignement `
        -roleDefinitionId $ReaderAndDataAccess `
        -resourceId $sa.Id `
        -principalIds $principleIds
}

function New-RoleAssignement {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string] $roleDefinitionId,
        [Parameter(Mandatory=$true)]
        [string] $resourceId,
        [Parameter(Mandatory=$true)]
        [string[]] $principalIds
    )
    
    # Get the full roledefinition Id for the role by roleDefinitionId. Microsoft often changes rolenames but roleDefinitionId's are always the same.
    # az role definition list --output json --query "[?name=='7f951dda-4ed3-4680-a7ca-43fe172d538d'].{roleName:roleName, name:name, id:id}"
    
    $role = Invoke-AzCommand {
            az role definition list `
                --output json `
                --query "[?name=='$roleDefinitionId'].{roleName:roleName, name:name, id:id}"
    }| ConvertFrom-Json

    foreach ($principleId in $principalIds) {
        Write-Information "Creating roleassignement for principle [$principleId] on resource [$resourceId]..." -InformationAction Continue
        Invoke-AzCommand {
            az role assignment create `
                --role $role.id `
                --scope $resourceId `
                --assignee $principleId
        } | out-null
    }
}

function New-ResourceGroup{
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string] $subscriptionId,
        [Parameter(Mandatory=$true)]
        [string] $resourceGroup,
        [string] $location = "westeurope"
    )

        Write-Information "Creating resource group [$resourceGroup] in subscription [$subscriptionId]..." -InformationAction Continue
        $rg = Invoke-AzCommand { 
            az group create --subscription $subscriptionId `
                            --name $resourceGroup `
                            --location $location 
        } | ConvertFrom-Json

        # Write-Verbose $rg 
        return $rg
}

function New-StorageAccount{
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string] $subscriptionId,
        [Parameter(Mandatory=$true)]
        [string] $resourceGroup,
        [Parameter(Mandatory=$true)]
        [string] $storageAccountName,
        [string] $location = "westeurope"
        )

        Write-Information "Creating storage account [$storageAccountName] in resource group [$resourceGroup]..." -InformationAction Continue
        $sa = Invoke-AzCommand { 
            az storage account create --subscription $subscriptionId `
                                      --resource-group $resourceGroup `
                                      --name $storageAccountName `
                                      --sku Standard_RAGRS `
                                      --encryption-services blob `
                                      --allow-blob-public-access false `
                                      --default-action Deny
        } | ConvertFrom-Json

        # Write-Verbose $sa 
        return $sa
}

function New-PrivateEndpoint{
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string] $sa_private_enpoint_name,
        [Parameter(Mandatory=$true)]
        [string] $subnetId,
        [Parameter(Mandatory=$true)]
        [string] $resourceGroup,
        [Parameter(Mandatory=$true)]
        [string] $storageAccountId
        )

        Write-Information "Creating private-endpoint [$sa_private_enpoint_name] in resource group [$resourceGroup]..." -InformationAction Continue
        $pep = Invoke-AzCommand { 
            az network private-endpoint create --name $sa_private_enpoint_name `
                                               --resource-group $resourceGroup `
                                               --subnet $subnetId `
                                               --private-connection-resource-id $storageAccountId `
                                               --group-id blob `
                                               --connection-name "pep" 
            } | ConvertFrom-Json
        
        # Write-Verbose $pep 
        return $pep
}

function Get-StoragePrivateEndpointId{
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string] $name,
        [Parameter(Mandatory=$true)]
        [string] $resourceGroup
        )

        $storage_private_endpoint_id = Invoke-AzCommand { 
            az network private-endpoint show --name $sa_private_enpoint_name `
                                             --resource-group $resourceGroup `
                                             --query id `
                                             --output tsv 
        }
        # Write-Verbose "Storage private-endpoint ID :[$storage_private_endpoint_id]"
        return $storage_private_endpoint_id
}

function Get-NetworkInterfaceId{
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string] $name,
        [Parameter(Mandatory=$true)]
        [string] $resourceGroup
        )

        $network_interface_id = Invoke-AzCommand { 
            az network private-endpoint show --name $sa_private_enpoint_name `
                                             --resource-group $resourceGroup `
                                             --query 'networkInterfaces[0].id' `
                                             --output tsv 
        }  
        # Write-Verbose "Storage Network Interface ID :[$network_interface_id]"
        return $network_interface_id
}

function Get-NetworkIntefacePrivateIp{
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string] $networkInterfaceId
        )

        $storage_network_interface_private_ip = Invoke-AzCommand { 
            az resource show --ids $networkInterfaceId `
                            --api-version 2019-04-01 `
                            --query 'properties.ipConfigurations[0].properties.privateIPAddress' `
                            --output tsv 
        }

        # Write-Verbose "Storage Network Interface private IP :[$storage_network_interface_private_ip]"
        return $storage_network_interface_private_ip
}

function New-DnsRecord{
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string] $storageAccountName,
        [Parameter(Mandatory=$true)]
        [string] $privateDnsResourceGroupName,
        [Parameter(Mandatory=$true)]
        [string] $privateDnsSubscriptionId,
        [Parameter(Mandatory=$true)]
        [string] $storageAccountPrivateEndpointName,
        [Parameter(Mandatory=$true)]
        [string] $storageAccountPrivateIp
        )

        Write-Information "Retrieve private-dns record-sets for [$storageAccountName] in resource group [$privateDnsResourceGroupName] in subsction [$privateDnsSubscriptionId]..." -InformationAction Continue
        $dnsRecordName = Invoke-AzCommand { 
            az network private-dns record-set a list --subscription $privateDnsSubscriptionId `
                                                     --resource-group $privateDnsResourceGroupName `
                                                     --query "[?name=='$storageAccountName']" `
                                                     --zone-name privatelink.blob.core.windows.net 
        } | ConvertFrom-Json
        
        $shouldCreate=$null -eq $dnsRecordName;
        $shouldRecreate=${dnsRecordName}?.aRecords.Count -gt 0 -and ${dnsRecordName}?.aRecords[0].ipv4Address -ne $storageAccountPrivateIp;

        if($shouldRecreate){
            Write-Information "Deleting private-dns record-set for [$storageAccountName] in resource group [$privateDnsResourceGroupName] in subsction [$privateDnsSubscriptionId]..." -InformationAction Continue
            Invoke-AzCommand { 
                az network private-dns record-set a delete --subscription $privateDnsSubscriptionId `
                                                           --resource-group $privateDnsResourceGroupName `
                                                           --zone-name privatelink.blob.core.windows.net `
                                                           --name $storageAccountName `
                                                           --yes
            }
        }

        if($shouldCreate -or $shouldRecreate){
            Write-Information "Creating private-dns [$storageAccountPrivateEndpointName] in resource group [$privateDnsResourceGroupName] in subsction [$privateDnsSubscriptionId]..." -InformationAction Continue
            $dnsRecord = Invoke-AzCommand { 
                az network private-dns record-set a add-record --subscription $privateDnsSubscriptionId `
                                                               --resource-group $privateDnsResourceGroupName `
                                                               --record-set-name $storageAccountName `
                                                               --zone-name privatelink.blob.core.windows.net `
                                                               --ipv4-address $storageAccountPrivateIp 
            } | ConvertFrom-Json
        }
        return $dnsRecord
}

function New-StorageContainer{
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string] $containerName,
        [Parameter(Mandatory=$true)]
        [string] $storageAccountName,
        [Parameter(Mandatory=$true)]
        [string] $subscriptionId,
        [Parameter(Mandatory=$true)]
        [string] $resourceGroup
        )

        Write-Information "Create container [$containerName] in storage account [$storageAccountName]" -InformationAction Continue
        $container = Invoke-AzCommand {
            az storage container create --subscription $subscriptionId  `
                                        --resource-group $resourceGroup `
                                        --account-name $storageAccountName `
                                        --name $containerName `
                                        --auth-mode login
         } | ConvertFrom-Json
        
        # Write-Verbose $container
        return $container
}

#Whenever an exception is thrown, the script will exit with a non-zero exit code.
$ErrorActionPreference = 'Stop'

Write-Information "SubnetId [$subnetId]" -InformationAction Continue
Write-Information "SubscriptionId [$subscriptionId]" -InformationAction Continue
Write-Information "ResourceGroup [$resourceGroup]" -InformationAction Continue
Write-Information "StorageAccountName [$storageAccountName]" -InformationAction Continue
Write-Information "Location [$location]" -InformationAction Continue
Write-Information "ContainerName [$containerName]" -InformationAction Continue
Write-Information "PrivateDnsSubscriptionId [$privateDnsSubscriptionId]" -InformationAction Continue
Write-Information "PrivateDnsResourcGroupName [$privateDnsResourceGroupName]" -InformationAction Continue
Write-Information "PrincipleIds [$principleIds]" -InformationAction Continue


New-TerraformStateStorageAccount -subscriptionId $subscriptionId `
                                -resourceGroup $resourceGroup `
                                -storageAccountName $storageAccountName `
                                -location $location `
                                -containerName $containerName `
                                -subnetId $subnetId `
                                -privateDnsSubscriptionId $privateDnsSubscriptionId `
                                -privateDnsResourceGroupName $privateDnsResourceGroupName `
                                -principleIds $principleIds