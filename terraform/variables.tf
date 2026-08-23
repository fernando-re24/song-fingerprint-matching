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

variable "matching_endpoint_backend_path" {
  description = "API Gateway path part for the song matching endpoint (no leading slash)."
  type        = string
  default     = "matches"
}

variable "uploading_endpoint_backend_path" {
  description = "API Gateway path part for the audio upload endpoint (no leading slash)."
  type        = string
  default     = "uploads"
}

variable "audio_bucket_name" {
  description = "Name of the audi uplaod bucket"
  type = string
  default = null
}
