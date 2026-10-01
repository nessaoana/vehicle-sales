resource "aws_s3_bucket" "assets" {
  bucket = var.assets_bucket_name

  tags = {
    service     = "vehicle-sales"
    environment = "localstack"
  }
}

resource "aws_s3_bucket_versioning" "assets" {
  bucket = aws_s3_bucket.assets.id

  versioning_configuration {
    status = "Enabled"
  }
}
