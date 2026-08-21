terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }

    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }

    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.6"
    }

    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
  }
}

locals {
  required_tags = {
    project    = "song-matcher"
    managed-by = "terraform"
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  # automatically tags all taggable provisioned resources
  default_tags {
    tags = local.required_tags
  }
}
