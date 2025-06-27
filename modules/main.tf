terraform {
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.45" # or latest
    }
  }
}

provider "hcloud" {
  token = var.hcloud_token
}

data "hcloud_ssh_key" "nat" {
  name = "nat-dev-key"
}

resource "hcloud_server" "llm_node" {
  name        = "llm-node"
  image       = "ubuntu-24.04"
  server_type = "cpx21"
  location    = "hel1"
  ssh_keys    = [data.hcloud_ssh_key.nat.id]
}

