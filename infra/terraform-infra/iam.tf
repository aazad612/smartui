resource "google_service_account" "app_sa" {
  account_id   = "${var.app_name}-sa"
  display_name = "${var.project_id} ${var.app_name}-sa"
}

resource "google_project_iam_member" "app_sa_roles" {
  for_each = toset(var.sa_roles)

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}
