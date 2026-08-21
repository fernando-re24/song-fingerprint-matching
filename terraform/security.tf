resource "aws_kms_key" "dynamodb_key" {
  description             = "KMS key for encrypting the songs table"
  deletion_window_in_days = 7
  enable_key_rotation     = true
}
