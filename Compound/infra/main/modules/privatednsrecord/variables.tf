variable "dns_zone_name" {
  description = "Name of the DNS Zone in which the record is creade"
  type        = string
}

variable "resource_group_name" {
}

variable "name" {
}

variable "dns_records" {
  type = list(object({
    fqdn         = string
    ip_addresses = list(string)
  }))
}
