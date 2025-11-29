resource "google_artifact_registry_repository" "app_repo" {
  project       = var.project_id
  location      = var.region
  repository_id = "${var.app_name}-repo"
  format        = "DOCKER"
  description   = "Docker images for ${var.app_name}"
}
