# Example Azure Storage setup. Review resources and permissions before applying.
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

variable "subscription_id" { type = string }
variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "storage_account_name" {
  type        = string
  description = "Globally unique lowercase Azure storage account name"
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

resource "azurerm_storage_account" "lakehouse_demo" {
  name                            = var.storage_account_name
  resource_group_name             = var.resource_group_name
  location                        = var.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
}

resource "azurerm_storage_container" "bronze" {
  name                  = "bronze"
  storage_account_id    = azurerm_storage_account.lakehouse_demo.id
  container_access_type = "private"
}
