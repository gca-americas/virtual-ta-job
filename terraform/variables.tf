variable "project_id" {
  description = "The Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "The deployment region"
  type        = string
  default     = "us-central1"
}

variable "github_org" {
  description = "The GitHub Organization hosting the workshop-ta-job repository (e.g. gca-americas)"
  type        = string
}

variable "db_connection_name" {
  description = "Cloud SQL Connection String"
  type        = string
  default     = "your-project_id:us-central1:events-db-instance"
}

variable "db_user" {
  type    = string
  default = "admin"
}

variable "db_pass" {
  type    = string
  default = "ChangeMe1234"
}

variable "db_name" {
  type    = string
  default = "event_db"
}
