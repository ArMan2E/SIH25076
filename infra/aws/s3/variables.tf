variable "region" {
  default     = "eu-north-1"
  description = "Region where aws bucked created"
}

variable "bucket_name" {
  default = "krishi-bkt-aryamandal63111"
}

variable "render_backend_role_arn" {
  description = "IAM role ARN of the Render backend"
  type        = string
}
