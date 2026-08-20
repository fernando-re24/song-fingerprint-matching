variable "aws_region" {
  description = "AWS region to deploy resources to."
  type        = string
  default     = "us-east-2"
}

variable "aws_profile" {
  description = "Optional local AWS CLI profile name (for example: dev, personal, or sso-profile)."
  type        = string
  default     = null
}

variable "matching_endpoint_backend_path"{
  description =  "Endpoint path for the song matching api"
  type = string
  default = null
}

variable "uploading_endpoint_backend_path"{
  description =  "Endpoint path for the song matching api"
  type = string
  default = null
}