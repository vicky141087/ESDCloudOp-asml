locals {
  resource_group_name = "compound-${var.short_name}-rg"
  static_site_name    = "compound-${var.short_name}-web"
}

module "environment" {
  source              = "./modules/environment"
  resource_group_name = local.resource_group_name
}

module "swa" {
  source              = "./modules/swa"
  resource_group_name = module.environment.resource_group_name
  static_site_name    = local.static_site_name
  subnet_id           = var.subnet_app_id
}

module "private_endpoint_dns_record" {
  source              = "./modules/privatednsrecord"
  name                = local.static_site_name    
  dns_zone_name       = "privatelink.1.azurestaticapps.net"
  dns_records         = module.swa.custom_dns
  resource_group_name = var.resource_group_name_ccoe
  providers = {
    azurerm.ccoe = azurerm.asmlmgt01ccoe #could also just use a subscription override, service principle stays the same
  }
}
