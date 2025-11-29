terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "johneys-tf-states"
    prefix = "smartui-infra/tfstate"
  }
}


