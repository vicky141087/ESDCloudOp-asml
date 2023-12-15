
resource "azurerm_private_dns_a_record" "pep_a_record_registry" {
  count               = 1 #Need to explicitly give the number of dns records to be expected, otherwise terraform error unable to evaluate unknown resources
  name                = split(".",var.dns_records[count.index].fqdn)[0]
  zone_name           = var.dns_zone_name
  resource_group_name = "dns-mgt01-rg"
  ttl                 = 3600
  records             = var.dns_records[count.index].ip_addresses

  provider = azurerm.ccoe

  lifecycle {
    ignore_changes = [tags]
  }
}
