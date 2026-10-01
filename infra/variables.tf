variable "aws_region" {
  description = "AWS region used by LocalStack."
  type        = string
  default     = "us-east-1"
}

variable "localstack_endpoint" {
  description = "LocalStack edge endpoint."
  type        = string
  default     = "http://localhost:4566"
}

variable "aws_access_key" {
  description = "AWS-compatible access key used by LocalStack."
  type        = string
  default     = "test"
}

variable "aws_secret_key" {
  description = "AWS-compatible secret key used by LocalStack."
  type        = string
  default     = "test"
  sensitive   = true
}

variable "assets_bucket_name" {
  description = "S3 bucket used by vehicle-sales."
  type        = string
  default     = "vehicle-sales-assets"
}
