# Johney LLM Hub (Regenerated)

Cloud Run-hosted web UI to talk to OpenAI, Perplexity, and Gemini,
with all conversations stored centrally in Firestore.

## Structure

- `config/config.yaml` – app configuration.
- `app/` – FastAPI backend.
- `web/templates/index.html` – HTML UI.
- `web/static/css/styles.css` – styles.
- `web/static/js/app.js` – frontend logic.
- `docker/Dockerfile` – container image for Cloud Run.
- `infra/terraform-infra` – infra layer (APIs, Artifact Registry, SA, IAM).
- `infra/terraform-app` – app layer (Cloud Run service + public IAM).

## Terraform – Infra Layer

```bash
cd infra/terraform-infra
cp terraform.tfvars.example terraform.tfvars
# edit: project_id, region, service_name if needed
terraform init
terraform apply
```

This will:
- Enable required APIs.
- Create Artifact Registry repo `llm-hub` in the given region.
- Create Cloud Run service account `llm-hub-ui-sa`.
- Grant `roles/datastore.user` on the project to that SA.

## Build Image

Build and push the image to Artifact Registry (keeping tag in sync with `image_tag` in app tfvars):

```bash
cd /path/to/llm-hub-ui-regenerated

gcloud builds submit   --region=us-central1   --tag us-central1-docker.pkg.dev/johneysadminproject/llm-hub/llm-hub-ui:v1   --file docker/Dockerfile .
```

## Terraform – App Layer

```bash
cd infra/terraform-app
cp terraform.tfvars.example terraform.tfvars
# edit: project_id, region, service_name, image_tag if needed
terraform init
terraform apply
```

This will:
- Create or update the Cloud Run v2 service.
- Use the image from Artifact Registry.
- Make the service publicly invokable (`roles/run.invoker` to `allUsers`).

## Local Development

```bash
pip install -r requirements.txt
export GCP_PROJECT_ID="johneysadminproject"
export OPENAI_API_KEY="..."
export PPLX_API_KEY="..."
export GEMINI_API_KEY="..."
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/
