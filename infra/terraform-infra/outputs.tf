output "app_repo_id" {
  description = "Artifact Registry repository id for the app"
  value       = google_artifact_registry_repository.app_repo.repository_id
}

output "app_repo_url" {
  description = "Artifact Registry repository URL for the app"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.app_repo.repository_id}"
}

output "app_sa_email" {
  description = "Service account email for the app"
  value       = google_service_account.app_sa.email
}

output "app_bucket_name" {
  description = "GCS bucket name for the app"
  value       = google_storage_bucket.app_bucket.name
}
