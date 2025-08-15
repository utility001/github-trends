variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "githubtrends"
}

variable "rds_db_name" {
    description = "RDS Database name"
  type        = string
  default     = "githubtrends"
}

variable "redshift_warehouse_name" {
    description = "Redshift Database name"
  type        = string
  default     = "githubtrends"
}