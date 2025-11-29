resource "google_firestore_database" "default" {
  project     = var.project_id
  name        = "(default)"

  # Firestore supports only a subset of regions
  # You MUST use a valid Firestore region
  location_id = var.firestore_region

  type = "FIRESTORE_NATIVE"
}
