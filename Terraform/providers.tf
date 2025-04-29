terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.89.0"
    }
    random = {
      source  = "hashicorp/random"
    }
  }

  required_version = ">= 1.5.0"
}

provider "azurerm" {
  features {}
}
