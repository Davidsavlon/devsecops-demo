# Azure Terraform IaC with intentional misconfigurations for DevSecOps testing

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "devsecops-demo-rg"
  location = "East US"
}

# ISSUE 1: Storage account with public blob access enabled
resource "azurerm_storage_account" "app_storage" {
  name                     = "devsecopsdemostorage"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  # Misconfiguration: public blob access allowed
  allow_nested_items_to_be_public = true

  # Misconfiguration: no HTTPS enforcement
  enable_https_traffic_only = false

  # Misconfiguration: no minimum TLS version
  min_tls_version = "TLS1_0"

  # Misconfiguration: no blob soft delete
  blob_properties {
    delete_retention_policy {
      days = 0
    }
  }
}

# ISSUE 2: Storage container with public access
resource "azurerm_storage_container" "app_container" {
  name                  = "appdata"
  storage_account_name  = azurerm_storage_account.app_storage.name
  container_access_type = "blob"
}

# ISSUE 3: Network Security Group allowing all inbound traffic
resource "azurerm_network_security_group" "web_nsg" {
  name                = "web-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  # Misconfiguration: SSH open to internet
  security_rule {
    name                       = "allow-ssh"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # Misconfiguration: RDP open to internet
  security_rule {
    name                       = "allow-rdp"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "3389"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # Misconfiguration: all ports open to internet
  security_rule {
    name                       = "allow-all"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "0.0.0.0/0"
    destination_address_prefix = "*"
  }
}

# ISSUE 4: Virtual machine with no disk encryption
resource "azurerm_linux_virtual_machine" "web_vm" {
  name                = "web-vm"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "Standard_B1s"
  admin_username      = "adminuser"

  # Misconfiguration: password auth enabled (should use SSH keys only)
  disable_password_authentication = false
  admin_password                  = "Password123!"

  network_interface_ids = []

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
    # Misconfiguration: disk encryption disabled
  }

  source_image_reference {
    publisher = "Canonical"
