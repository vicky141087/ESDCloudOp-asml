provider "azurerm" {
   features {}
}

provider "azurerm" {
  features {}
  alias                      = "asmlmgt01ccoe"
  subscription_id            = "19a5edd0-42d3-4b5f-88b5-45f718494ad3"
  skip_provider_registration = true
}