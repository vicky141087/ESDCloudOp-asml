param
(
    [Parameter(Mandatory=$true)]
    [string] $Key,
    [Parameter(Mandatory=$true)]
    [string] $PrivateDnsSubscriptionId,
    [Parameter(Mandatory=$true)]
    [string] $PrivateDnsResourceGroupName
)

$resourcesToDelete = az resource list --resource-group compound-$Key-rg --query "[].[id]" | ConvertFrom-Json
$resourcesToDelete | Foreach-Object {
    Write-host "Deleting resource $_..."
    az resource delete --resource-group myResourceGroup --ids $_ --verbose
}

while (az resource list --resource-group compound-$Key-rg --query "[].[id]" --output tsv) {
    Write-Host "waiting for delete to finish"    
    Start-Sleep 10
}

az account set --subscription $PrivateDnsSubscriptionId
az network private-dns record-set cname delete --resource-group $PrivateDnsResourceGroupName --zone-name privatelink.1.azurestaticapps.net --name "compound-$Key-web" --yes

Write-host "Done."

 