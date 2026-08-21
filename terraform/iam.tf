resource "aws_iam_policy" "fargate_dynamodb_access" {
  name        = "fargate-dynamodb-access"
  description = "Allows the fargate instance to read from the songs table"
  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      # TODO: re-add an "AssumeSongTableRole" statement once the role ARN it
      # should target exists. An IAM statement cannot have an empty Resource
      # list, so it is left out rather than stubbed.
      {
        Sid    = "ReadSongsTable"
        Effect = "Allow"
        Action = [
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:GetItem",
          "dynamodb:BatchGetItem",
          "dynamodb:DescribeTable"
        ]
        Resource = [
          aws_dynamodb_table.songs_db.arn,
          "${aws_dynamodb_table.songs_db.arn}/index/*"
        ]
      },
      {
        Sid    = "UseDynamoDbKmsKey"
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:Encrypt",
          "kms:GenerateDataKey",
          "kms:DescribeKey"
        ]
        Resource = aws_kms_key.dynamodb_key.arn
      }
    ]
  })
}


resource "aws_iam_role" "fingerprintGenerator" {
  name = "fingerprint-generator-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "fingerprint_generator_basic_execution" {
  role       = aws_iam_role.fingerprintGenerator.name
  policy_arn = "arn:${data.aws_partition.current.partition}:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "audio_upload_bucket_policy" {
  statement {
    actions = ["s3:GetObject"]

    # Object-level actions must target objects, not the bucket itself.
    resources = ["${aws_s3_bucket.audio_upload_bucket.arn}/*"]

    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.fingerprintGenerator.arn]
    }
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["true"]
    }
  }
}

resource "aws_s3_bucket_policy" "audio_upload_bucket_policy" {
  bucket = aws_s3_bucket.audio_upload_bucket.id
  policy = data.aws_iam_policy_document.audio_upload_bucket_policy.json
}

resource "aws_iam_role" "presignedURL" {
  name = "presigned-url-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "presigned_url_basic_execution" {
  role       = aws_iam_role.presignedURL.name
  policy_arn = "arn:${data.aws_partition.current.partition}:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Access to the upload bucket for the presigned URL signer. This belongs in an
# inline/managed policy: an assume_role_policy only describes who may assume
# the role, never what the role may do.
resource "aws_iam_role_policy" "presigned_url_bucket_access" {
  name = "presigned-url-bucket-access"
  role = aws_iam_role.presignedURL.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "WriteAudioUploads"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ]
        Resource = [
          "${aws_s3_bucket.audio_upload_bucket.arn}/*"
        ]
      }
    ]
  })
}
