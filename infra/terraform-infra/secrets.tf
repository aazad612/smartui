resource "google_secret_manager_secret" "openai_api_key" {
  project   = var.project_id
  secret_id = "${var.app_name}-openai-api-key"

    replication {
        auto {}
    }

}

resource "google_secret_manager_secret_iam_member" "openai_accessor" {
  secret_id = google_secret_manager_secret.openai_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.app_sa.email}"
}


resource "google_secret_manager_secret" "notion_api_key" {
  project   = var.project_id
  secret_id = "${var.app_name}-notion-api-key"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_iam_member" "notion_accessor" {
  secret_id = google_secret_manager_secret.notion_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.app_sa.email}"
}
