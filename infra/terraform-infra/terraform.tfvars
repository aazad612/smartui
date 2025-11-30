project_id   = "johneysadminproject"
region       = "us-central1"
app_name = "llm-hub"
firestore_region = "us-central1"

sa_roles = [
  "roles/datastore.user",
  "roles/storage.objectAdmin",
  "roles/logging.logWriter",
  "roles/monitoring.metricWriter",
  "roles/aiplatform.user"
]

enabled_apis = [
  "run.googleapis.com",
  "artifactregistry.googleapis.com",
  "firestore.googleapis.com",
  "cloudbuild.googleapis.com",
  "iam.googleapis.com",
  "secretmanager.googleapis.com",
  "aiplatform.googleapis.com",
  "generativelanguage.googleapis.com"
]

vertex_location = "us-central1"
vertex_model_id = "gemini-1.5-pro"
