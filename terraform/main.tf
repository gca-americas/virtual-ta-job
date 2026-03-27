terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

data "google_project" "project" {
}

# 1. Enable Pub/Sub API
resource "google_project_service" "pubsub_api" {
  project = var.project_id
  service = "pubsub.googleapis.com"
  disable_on_destroy = false
}

# 2. Enable Cloud Build API
resource "google_project_service" "cloudbuild_api" {
  project = var.project_id
  service = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

# 2.5 Enable Secret Manager API
resource "google_project_service" "secretmanager_api" {
  project = var.project_id
  service = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

# 3. Enable Cloud Scheduler API
resource "google_project_service" "cloudscheduler_api" {
  project = var.project_id
  service = "cloudscheduler.googleapis.com"
  disable_on_destroy = false
}

# 3.5 Enable Cloud Run API
resource "google_project_service" "run_api" {
  project = var.project_id
  service = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "aiplatform_api" {
  project            = var.project_id
  service            = "aiplatform.googleapis.com"
  disable_on_destroy = false
}

# 3. Deploy Queue Topic
resource "google_pubsub_topic" "deploy_queue" {
  name       = "deploy_queue"
  project    = var.project_id
  depends_on = [google_project_service.pubsub_api]
}

# 4. Demolish Queue Topic
resource "google_pubsub_topic" "demolish_queue" {
  name       = "demolish_queue"
  project    = var.project_id
  depends_on = [google_project_service.pubsub_api]
}

# 5. Cloud Build Trigger for Deploy
resource "google_cloudbuild_trigger" "deploy_trigger" {
  name        = "deploy-event-pipeline"
  description = "Trigger cloudbuild-deploy.yaml upon deploy_queue PubSub event"
  project     = var.project_id
  
  pubsub_config {
    topic = google_pubsub_topic.deploy_queue.id
  }

  substitutions = {
    _BODY = "$(body.message.data)"
  }

  source_to_build {
    uri       = "https://github.com/${var.github_org}/virtual-ta-job"
    ref       = "refs/heads/main"
    repo_type = "GITHUB"
  }

  filename        = "cloudbuild-deploy.yaml"
  service_account  = google_service_account.virtual_ta_job.id
  depends_on      = [google_project_service.cloudbuild_api]
}

# 6. Cloud Build Trigger for Demolish
resource "google_cloudbuild_trigger" "demolish_trigger" {
  name        = "demolish-event-pipeline"
  description = "Trigger cloudbuild-demolish.yaml upon demolish_queue PubSub event"
  project     = var.project_id
  
  pubsub_config {
    topic = google_pubsub_topic.demolish_queue.id
  }

  substitutions = {
    _BODY = "$(body.message.data)"
  }

  source_to_build {
    uri       = "https://github.com/${var.github_org}/virtual-ta-job"
    ref       = "refs/heads/main"
    repo_type = "GITHUB"
  }

  filename        = "cloudbuild-demolish.yaml"
  service_account  = google_service_account.virtual_ta_job.id
  depends_on      = [google_project_service.cloudbuild_api]
}

# 8.5 Service Account Identity Execution Profile
resource "google_service_account" "virtual_ta_job" {
  account_id   = "virtual-ta-job-sa"
  display_name = "Virtual Technical Assistant Job Orchestrator"
  project      = var.project_id
}

# 8.6 Strict IAM Privileges
resource "google_project_iam_member" "sa_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.virtual_ta_job.email}"
}

resource "google_project_iam_member" "sa_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.virtual_ta_job.email}"
}

resource "google_project_iam_member" "sa_iam_saUser" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.virtual_ta_job.email}"
}

resource "google_project_iam_member" "sa_ar_admin" {
  project = var.project_id
  role    = "roles/artifactregistry.admin"
  member  = "serviceAccount:${google_service_account.virtual_ta_job.email}"
}

resource "google_project_iam_member" "sa_storage" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.virtual_ta_job.email}"
}

resource "google_project_iam_member" "sa_cb_editor" {
  project = var.project_id
  role    = "roles/cloudbuild.builds.editor"
  member  = "serviceAccount:${google_service_account.virtual_ta_job.email}"
}

resource "google_project_iam_member" "sa_service_usage" {
  project = var.project_id
  role    = "roles/serviceusage.serviceUsageConsumer"
  member  = "serviceAccount:${google_service_account.virtual_ta_job.email}"
}

resource "google_project_iam_member" "sa_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.virtual_ta_job.email}"
}

resource "google_project_iam_member" "sa_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.virtual_ta_job.email}"
}

resource "google_project_iam_member" "sa_logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.virtual_ta_job.email}"
}

# 8.7 Cloud Build Service Agent Pub/Sub Binding
resource "google_project_iam_member" "cb_sa_pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-cloudbuild.iam.gserviceaccount.com"
}

# 9. Native Cloud Run Job (Hourly execution platform)
resource "google_cloud_run_v2_job" "hourly_job" {
  name     = "hourly-job"
  location = var.region
  project  = var.project_id

  template {
    template {
      service_account = google_service_account.virtual_ta_job.email
      containers {
        # Note: We rely on the initial gcloud run jobs deploy from our setup.md
        # to generate the native code image. This prevents container teardowns.
        image = "us-docker.pkg.dev/cloudrun/container/job:latest"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      template[0].template[0].containers[0].image,
      template[0].template[0].containers[0].env,
      client,
      client_version,
    ]
  }

  depends_on = [google_project_service.run_api]
}

# 9. Cloud Scheduler execution loop
resource "google_cloud_scheduler_job" "hourly_cron" {
  name        = "hourly-job-trigger"
  description = "Triggers the hourly execution loop natively via Cloud Run Job REST APIs"
  schedule    = "0 * * * *"
  project     = var.project_id
  region      = var.region
  
  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/hourly-job:run"

    oauth_token {
      service_account_email = google_service_account.virtual_ta_job.email
    }
  }
  
  depends_on = [google_project_service.cloudscheduler_api, google_cloud_run_v2_job.hourly_job]
}
