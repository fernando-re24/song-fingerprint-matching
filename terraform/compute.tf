locals {
  # The lambda source lives under backend/, not at the repo root.
  fingerprint_module_path      = "${path.module}/../backend/fingerprintGenerator"
  fingerprint_requirements     = "${path.module}/../backend/requirements.txt"
  fingerprint_lambda_build_dir = "${path.module}/build/fingerprintGenerator"
  fingerprint_lambda_zip       = "${path.module}/build/fingerprintGenerator.zip"

  presigned_url_module_path      = "${path.module}/../presignedURL"
  presigned_url_requirements     = "${path.module}/../presignedURL/requirements.txt"
  presigned_url_lambda_build_dir = "${path.module}/build/presignedURL"
  presigned_url_lambda_zip       = "${path.module}/build/presignedURL.zip"
}

resource "aws_lambda_function" "fingerprint_generator" {
  function_name = "fingerprintGenerator"
  role          = aws_iam_role.fingerprintGenerator.arn

  filename         = data.archive_file.fingerprint_generator.output_path
  handler          = "fingerprintGenerator.__main__.lambda_handler"
  source_code_hash = data.archive_file.fingerprint_generator.output_base64sha256
  runtime          = "python3.11"
  architectures    = ["arm64"]
  memory_size      = 512
  timeout          = 10

  depends_on = [data.archive_file.fingerprint_generator]
}

# Artifact

resource "null_resource" "fingerprint_generator_build" {

  # Rebuild artifact if the requirements or code change
  triggers = {
    requirements = filesha256(local.fingerprint_requirements)
    source_code = sha256(join("", [
      for file in fileset(local.fingerprint_module_path, "**/*.py") :
      filesha256("${local.fingerprint_module_path}/${file}")
    ]))
  }

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    command     = <<-EOT
      set -euo pipefail

      # Remove old build and copy in updated files. The module is nested one
      # level deep so the package name stays part of the handler path.
      rm -rf "${local.fingerprint_lambda_build_dir}"
      mkdir -p "${local.fingerprint_lambda_build_dir}"
      cp -r "${local.fingerprint_module_path}" "${local.fingerprint_lambda_build_dir}/"

      # Check for pip installation
      if ! python3 -m pip --version >/dev/null 2>&1; then
          echo "ERROR: python3 has no pip module. On Debian/Ubuntu run:" >&2
          echo "sudo apt-get update && sudo apt-get install -y python3-pip" >&2
          exit 1
      fi

      # Install dependencies
      python3 -m pip install \
          -r "${local.fingerprint_requirements}" \
          --target "${local.fingerprint_lambda_build_dir}"
    EOT
  }
}

data "archive_file" "fingerprint_generator" {
  type        = "zip"
  source_dir  = local.fingerprint_lambda_build_dir
  output_path = local.fingerprint_lambda_zip
  depends_on  = [null_resource.fingerprint_generator_build]
}


# Presigned url generator
resource "aws_lambda_function" "presignedURL" {
  function_name = "presignedURL"
  role          = aws_iam_role.presignedURL.arn

  filename         = data.archive_file.presignedURL.output_path
  handler          = "presignedURL.__main__.lambda_handler"
  source_code_hash = data.archive_file.presignedURL.output_base64sha256
  runtime          = "python3.11"
  architectures    = ["arm64"]
  memory_size      = 512
  timeout          = 10

  depends_on = [data.archive_file.presignedURL]
}

resource "null_resource" "presigned_url_generator_build" {

  # Rebuild artifact if the requirements or code change
  triggers = {
    requirements = filesha256(local.presigned_url_requirements)
    source_code = sha256(join("", [
      for file in fileset(local.presigned_url_module_path, "**/*.py") :
      filesha256("${local.presigned_url_module_path}/${file}")
    ]))
  }

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    command     = <<-EOT
      set -euo pipefail

      # Remove old build and copy in updated files
      rm -rf "${local.presigned_url_lambda_build_dir}"
      mkdir -p "${local.presigned_url_lambda_build_dir}"
      cp -r "${local.presigned_url_module_path}" "${local.presigned_url_lambda_build_dir}/"

      # Check for pip installation
      if ! python3 -m pip --version >/dev/null 2>&1; then
          echo "ERROR: python3 has no pip module. On Debian/Ubuntu run:" >&2
          echo "sudo apt-get update && sudo apt-get install -y python3-pip" >&2
          exit 1
      fi

      # Install dependencies
      python3 -m pip install \
          -r "${local.presigned_url_requirements}" \
          --target "${local.presigned_url_lambda_build_dir}"
    EOT
  }
}

data "archive_file" "presignedURL" {
  type        = "zip"
  source_dir  = local.presigned_url_lambda_build_dir
  output_path = local.presigned_url_lambda_zip
  depends_on  = [null_resource.presigned_url_generator_build]
}
