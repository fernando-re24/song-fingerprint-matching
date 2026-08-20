resource "aws_lambda_function" "fingerprint_generator"{
    function_name = "fingerprintGenerator"
    role = ""

    filename = data.archive_file.fingerprint_generator.outputh_path
    handler = "fingerprintGenerator.__main__.lambda_handler"
    source_code_hash = data.archive_file.fingerprint_generator.output_base64sha256
    runtime = "python3"
    architectures                  = ["arm64"]
    memory_size                    = 512
    timeout                        = 10

    depends_on = [ data.archive_file.fingerprint_generator ]
}

# Artifact
locals {
    fingerprint_module_path = "${path.modulle}/../fingerprintGenerator"
    lambda_build_dir = "${path.module/build/fingerprintGenerator}"
    lambda_zip = "${path.module}/build/fingerprintGenerator.zip"
}

resource "null_resource" "fingerprint_generator_build" {

    # Rebuild artifact if the requirements or code change
    triggers = {
        requirements = filesha256("${local.fingerprint_module_path}/requirements.txt")
        source_code = sha256(join("",[
            for file in fileset(local.fingerprint_module_path, "/*.py"):
                filesha256("${local.fingerprint_module_path}/${file}")
        ]))
    }

    provisioner "local-exec" {
        interpreter = [ "/bin/bash", "-c" ]
        command = <<-EOT
            set -euo pipefail

            # Remove old build and copy in updated files
            rm -rf "${local.lambda_build_dir}
            cp -r "${fingerprint_module_path}" "${local.lambda_build_dir}"

            # Check for pip installation
            if ! python3 -m pip --version/dev/null 2>&1; then
                echo "ERROR: python3 has no pip module. On Debian/Ubuntu run:" >&2
                echo "sudo apt-get update && sudo apt-get install -y python3-pip" >&2
                exit 1
            fi

            # Install dependencies
            python3 -m pip install \
                -r "${local.fingerprint_module_path}/requirements.txt \
                --target "${local.lambda_build_dir} \ 
        EOT
      
    }
}

data "archive_file" "fingerprint_generator" {
    type = "zip"
    source_dir =  local.lambda_build_dir
    output_path = local.lambda_zip
    depends_on = [null_resource.fingerprint_generator_build]
}