resource "aws_iam_policy" "fargate_dynamodb_access"{
    name = "fargate-dynamodb-access"
    description = "Allows the fargate instance to read from the songs table"
    policy = jsonencode({
        Version = "2012-10-17"

        {
        Sid    = "AssumeSourceTableRole"
        Effect = "Allow"
        Action = [
          "sts:AssumeRole"
        ]
        Resource = [
          var.source_table_assume_role_arn
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
  })
}
