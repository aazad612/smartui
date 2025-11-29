terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "johneys-tf-states"
    prefix = "smartui-app/tfstate"
  }
}


provider "google" {
  project = var.project_id
  region  = var.region
}