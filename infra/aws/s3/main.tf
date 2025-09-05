terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.10.0"
    }
  }
}

provider "aws" {
  region = var.region
}
// create the resource
resource "aws_s3_bucket" "krishi_bucket" {
  bucket        = var.bucket_name
  force_destroy = true
}
// add cors policy resource to ensure frontend http endpoints can access for
// presigned url file uploads
# resource "aws_s3_bucket_cors_configuration" "krishi_bucket_CORS" {
#   bucket = aws_s3_bucket.krishi_bucket.id
#   cors_rule {
#     allowed_origins = ["*"] // bad habit give deployed origin
#     allowed_methods = ["PUT", "POST", "GET"]
#     allowed_headers = ["*"] // must put explicit headers
#   }
#   // can add multiple cors_rule blocks in a single bucket 
#   // but should not splt CORS rule accross multiple terraform resources for same bucked
# }

# policy for redner backend access
resource "aws_s3_bucket_policy" "allow_render_backend" {
  bucket = aws_s3_bucket.krishi_bucket.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowBackendUserPutGet"
        Effect = "Allow"
        Principal = {
          AWS = var.render_backend_role_arn
        }
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.krishi_bucket.arn}/*",
          "${aws_s3_bucket.krishi_bucket.arn}"
        ]
      }
    ]
  })
}
