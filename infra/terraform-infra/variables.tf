variable "project_id" {
  description = "GCP project id"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "app_name" {
  description = "Logical application name (used for repo, SA, bucket naming)"
  type        = string
}

variable "sa_roles" {
  description = "List of IAM roles to grant to the app service account at project level"
  type        = list(string)
}

variable "enabled_apis" {
  description = "List of GCP APIs to enable"
  type        = list(string)
}

variable "firestore_region" {
  description = "Region for Firestore. Must be a valid Firestore region (ex: us-central1, us-east1)"
  type        = string
}