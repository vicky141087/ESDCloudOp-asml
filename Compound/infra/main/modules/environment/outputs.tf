output "resource_group_name" {
  description = "Resource group name"
  value       = data.azurerm_resource_group.hosting.name
}

output "tags" {
  description = "Resource group tags"
  value       = data.azurerm_resource_group.hosting.tags
}

output "location" {
  description = "Resource group location"
  value       = data.azurerm_resource_group.hosting.location
}
