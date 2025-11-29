resource "google_storage_bucket" "app_bucket" {
  project  = var.project_id
  name     = "${var.project_id}-${var.app_name}"
  location = var.region

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}
