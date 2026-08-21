data "aws_caller_identity" "current" {}

data "aws_partition" "current" {}

resource "aws_api_gateway_rest_api" "song_api" {
  name = "song-api"
}

# Matching
resource "aws_api_gateway_resource" "matching_resource" {
  rest_api_id = aws_api_gateway_rest_api.song_api.id
  parent_id   = aws_api_gateway_rest_api.song_api.root_resource_id
  path_part   = var.matching_endpoint_backend_path
}

resource "aws_api_gateway_method" "matching-request-method" {
  rest_api_id   = aws_api_gateway_rest_api.song_api.id
  resource_id   = aws_api_gateway_resource.matching_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "matching-request-integration" {
  rest_api_id             = aws_api_gateway_rest_api.song_api.id
  resource_id             = aws_api_gateway_resource.matching_resource.id
  http_method             = aws_api_gateway_method.matching-request-method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.fingerprint_generator.invoke_arn
}

resource "aws_lambda_permission" "fingerprint_generator_request_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fingerprint_generator.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "arn:${data.aws_partition.current.partition}:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.song_api.id}/*/${aws_api_gateway_method.matching-request-method.http_method}${aws_api_gateway_resource.matching_resource.path}"
}

resource "aws_api_gateway_method" "matching-result-method" {
  rest_api_id   = aws_api_gateway_rest_api.song_api.id
  resource_id   = aws_api_gateway_resource.matching_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

# TODO: this method has no integration yet, so API Gateway will reject the
# deployment until one is added (see matching-request-integration above).

# Uploading
resource "aws_api_gateway_resource" "upload_resource" {
  rest_api_id = aws_api_gateway_rest_api.song_api.id
  parent_id   = aws_api_gateway_rest_api.song_api.root_resource_id
  path_part   = var.uploading_endpoint_backend_path
}

resource "aws_api_gateway_method" "upload-method" {
  rest_api_id   = aws_api_gateway_rest_api.song_api.id
  resource_id   = aws_api_gateway_resource.upload_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# TODO: wire this method to aws_lambda_function.presignedURL with an
# aws_api_gateway_integration + aws_lambda_permission pair, then add an
# aws_api_gateway_deployment / aws_api_gateway_stage so the API is reachable.
