variable "project" {
  description = "Project ID"
  type        = string
  # Vous pouvez même mettre une valeur par défaut ici si vous voulez éviter le -var à chaque fois
  default     = "taxi-rides-ny-485214" 
}

variable "region" {
  description = "Project Region"
  default     = "us-central1"
}

variable "location" {
  description = "Project Location"
  default     = "US"
}

variable "bq_dataset_name" {
  description = "My Big Query dataset"
  default     = "ny_taxi_bigquery_dataset"
}

variable "gcs_bucket_name" {
  description = "My Storage Bucket Name"
  default     = "taxi-rides-ny-485214-terra-bucket"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}