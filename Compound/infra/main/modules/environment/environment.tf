data "azurerm_resource_group" "hosting" {
  name = var.resource_group_name
}

data "azurerm_client_config" "current" {}
