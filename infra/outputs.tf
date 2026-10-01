output "assets_bucket_name" {
  description = "Provisioned S3 bucket name."
  value       = aws_s3_bucket.assets.bucket
}

output "localstack_endpoint" {
  description = "LocalStack endpoint used by Terraform."
  value       = var.localstack_endpoint
}
