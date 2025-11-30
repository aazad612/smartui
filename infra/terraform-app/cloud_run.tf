resource "google_cloud_run_v2_service" "app" {
  name     = "${var.app_name}-ui"
  location = var.region

  template {
    service_account = data.google_service_account.app_sa.email

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.app_name}-repo/${var.app_name}-ui:${var.image_tag}"

      env {
        name = "OPENAI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = "${var.app_name}-openai-api-key"
            version = "latest"
          }
        }
      }

      env {
        name = "NOTION_API_KEY"
        value_source {
          secret_key_ref {
            secret  = "${var.app_name}-notion-api-key"
            version = "latest"
          }
        }
      }
      
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
    }
  }
}
