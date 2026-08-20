output "matching_request_path" {
  value       = aws_api_gateway_resource.matching_resource.path
  description = "The API path the frontend sends matching requests to"
}
