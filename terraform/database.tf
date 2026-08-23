resource "aws_dynamodb_table" "songs_db" {
  name             = "songs-db"
  billing_mode     = "PAY_PER_REQUEST"
  hash_key         = "PK"
  range_key        = "SK"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  # Attribute definitions
  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  # Only key attributes (table keys + index keys) may be declared here.
  attribute {
    name = "hashIndex"
    type = "S"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb_key.arn
  }

  point_in_time_recovery {
    enabled = true
  }

  global_secondary_index {
    name            = "HashIndex"
    projection_type = "INCLUDE"

    # backend/services/matcher.py reads songId and offset off this index.
    non_key_attributes = ["songId", "offset"]

    key_schema {
      attribute_name = "hashIndex"
      key_type       = "HASH"
    }
  }
}

resource "aws_s3_bucket" "audio_upload_bucket" {
  bucket = var.audio_bucket_name
}

# Versioning disabled since audio uploads are ephemeral
resource "aws_s3_bucket_versioning" "audio_upload_bucket" {
  bucket = aws_s3_bucket.audio_upload_bucket.id

  versioning_configuration {
    status = "Suspended"
  }
}

resource "aws_s3_bucket_public_access_block" "audio_upload_bucket" {
  bucket = aws_s3_bucket.audio_upload_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# resource "aws_s3_bucket_lifecycle_configuration" "audio_upload_bucket_lifecycle" {
#   bucket = aws_s3_bucket.audio_upload_bucket.id
#   depends_on = [ aws_s3_bucket_versioning.audio_upload_bucket ]
#   # Remove delete markers orphaned after expired log versions are purged.
#   rule {
#     id     = "clean-expired-delete-markers"
#     status = "Enabled"

#     filter {}

#     expiration {
#       expired_object_delete_marker = true
#     }
#   }
# }

# TODO: Add redis
