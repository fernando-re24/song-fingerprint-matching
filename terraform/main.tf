resource "aws_api_gateway_rest_api" "song_api" {
    name = "song-api"
}


# Matching
resource "aws_api_gateway_resource" "matching_resource" {
    rest_api_id = aws_api_gateway_rest_api.song_api.id
    parent_id = aws_api_gateway_rest_api.song_api.root_resource_id
    path_part = var.matching_endpoint_backend_path

}

resource "aws_api_gateway_method" "matching-request-method" {
    rest_api_id = aws_api_gateway_rest_api.song_api.id
    resource_id = aws_api_gateway_resource.song_api_resource.id
    http_method = "POST"
    authorization = None
}

resource "aws_api_gateway_method" "matching-result-method" {
    rest_api_id = aws_api_gateway_rest_api.song_api.id
    resource_id = aws_api_gateway_resource.song_api_resource.id
    http_method = "GET"
    authorization = None
}



# Uploading
resource "aws_api_gateway_resource" "uopload_resource" {
    rest_api_id = aws_api_gateway_rest_api.song_api.id
    parent_id = aws_api_gateway_rest_api.song_api.root_resource_id
    path_part = var.uploading_endpoint_backend_path

}

resource "aws_api_gateway_method" "upload-method" {
    rest_api_id = aws_api_gateway_rest_api.song_api.id
    resource_id = aws_api_gateway_resource.song_api_resource.id
    http_method = "POST"
    authorization = None
}