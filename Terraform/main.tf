resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

# Storage Account
resource "azurerm_storage_account" "archive" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  access_tier              = "Cool"
}

# Storage Container for Archive
resource "azurerm_storage_container" "archive_container" {
  name                  = "archive"
  storage_account_name  = azurerm_storage_account.archive.name
  container_access_type = "private"
}

# Cosmos DB Account
resource "azurerm_cosmosdb_account" "main" {
  name                = var.cosmos_account_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"
  consistency_policy {
    consistency_level = "Session"
  }
  geo_location {
    location          = azurerm_resource_group.main.location
    failover_priority = 0
  }
}

# Cosmos Database
resource "azurerm_cosmosdb_sql_database" "main" {
  name                = var.cosmos_db_name
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
}

# Cosmos Container
resource "azurerm_cosmosdb_sql_container" "main" {
  name                  = var.cosmos_container_name
  resource_group_name   = azurerm_resource_group.main.name
  account_name          = azurerm_cosmosdb_account.main.name
  database_name         = azurerm_cosmosdb_sql_database.main.name
  partition_key_path    = "/billingId"
  throughput            = 400
}

# Key Vault
resource "azurerm_key_vault" "main" {
  name                        = var.key_vault_name
  location                    = azurerm_resource_group.main.location
  resource_group_name         = azurerm_resource_group.main.name
  sku_name                    = "standard"
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days  = 7
}

# App Service Plan for Function
resource "azurerm_service_plan" "main" {
  name                = "billing-func-plan"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = "Y1" # Consumption Plan
}

# Managed Identity
resource "azurerm_user_assigned_identity" "func_identity" {
  name                = "billing-func-identity"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
}

# Azure Function App
resource "azurerm_linux_function_app" "archive_function" {
  name                       = var.function_app_name
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  service_plan_id            = azurerm_service_plan.main.id
  storage_account_name       = azurerm_storage_account.archive.name
  storage_account_access_key = azurerm_storage_account.archive.primary_access_key
  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.func_identity.id]
  }
  app_settings = {
    "AzureWebJobsStorage" = azurerm_storage_account.archive.primary_connection_string
    "COSMOS_DB_ACCOUNT"   = azurerm_cosmosdb_account.main.name
    "COSMOS_DB_NAME"      = azurerm_cosmosdb_sql_database.main.name
    "COSMOS_CONTAINER"    = azurerm_cosmosdb_sql_container.main.name
    "STORAGE_ACCOUNT"     = azurerm_storage_account.archive.name
    "ARCHIVE_CONTAINER"   = azurerm_storage_container.archive_container.name
  }
}
