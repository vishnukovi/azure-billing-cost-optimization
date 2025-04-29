variable "location" {
  type    = string
  default = "East US"
}

variable "resource_group_name" {
  type    = string
  default = "billing-opt-rg"
}

variable "function_app_name" {
  type    = string
  default = "billing-archive-func"
}

variable "storage_account_name" {
  type    = string
  default = "billingarchivestorage"
}

variable "cosmos_account_name" {
  type    = string
  default = "billingcosmosdbaccount"
}

variable "cosmos_db_name" {
  type    = string
  default = "billingdb"
}

variable "cosmos_container_name" {
  type    = string
  default = "billingrecords"
}

variable "key_vault_name" {
  type    = string
  default = "billingsecretsvault"
}
