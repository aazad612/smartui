data "google_service_account" "app_sa" {
  project    = var.project_id
  account_id = "${var.app_name}-sa"
}
