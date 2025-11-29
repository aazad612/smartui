output "cloud_run_service_name" {
  description = "The deployed Cloud Run service name"
  value       = google_cloud_run_v2_service.app.name
}

output "cloud_run_url" {
  description = "Public URL of the Cloud Run service"
  value       = google_cloud_run_v2_service.app.uri
}

output "cloud_run_region" {
  description = "Region where the Cloud Run service is deployed"
  value       = var.region
}

output "service_account_email" {
  description = "Service account used by the Cloud Run service"
  value       = data.google_service_account.app_sa.email
}

output "container_image" {
  description = "Container image deployed to Cloud Run"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.app_name}-repo/${var.app_name}-ui:${var.image_tag}"
}
