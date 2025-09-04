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
resource "aws_s3_bucket" "presign_url_file_storage" {
  bucket        = var.bucket_name
  force_destroy = true
}
// add cors policy resource to ensure frontend http endpoints can access for
// presigned url file uploads
resource "aws_s3_bucket_cors_configuration" "presign_url_file_storage_CORS" {
  bucket = aws_s3_bucket.presign_url_file_storage.id
  cors_rule {
    allowed_origins = ["*"] // bad habit give deployed origin
    allowed_methods = ["PUT", "POST", "GET"]
    allowed_headers = ["*"] // must put explicit headers
  }
  // can add multiple cors_rule blocks in a single bucket 
  // but should not splt CORS rule accross multiple terraform resources for same bucked

}
