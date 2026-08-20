resource "aws_iam_policy" "fargate_dynamodb_access" {
  name        = "fargate-dynamodb-access"
  description = "Allows the fargate instance to read from the songs table"
  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "AssumeSongTableRole"
        Effect = "Allow"
        Action = [
          "sts:AssumeRole"
        ]
        Resource = [
          #
        ]
      },
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
