module "environment" {
  source              = "../environment"
  resource_group_name = var.resource_group_name
}

resource "azurerm_static_site" "web" {
  name = var.static_site_name
  resource_group_name = module.environment.resource_group_name
  location = module.environment.location
  sku_size = "Standard"

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_private_endpoint" "pep" {
  name                = "${var.static_site_name}-pep"
  resource_group_name = module.environment.resource_group_name
  location            = module.environment.location
  subnet_id           = var.subnet_id

  private_service_connection {
    name                           = "pep"
    is_manual_connection           = false
    private_connection_resource_id = resource.azurerm_static_site.web.id
    subresource_names              = ["staticSites"]
  }

  lifecycle {
    ignore_changes = [tags]
  }
}

