import boto3
import json
import logging
import os
import random
import uuid
from botocore.exceptions import ClientError

CONTENT_TYPE = "audio/"
MIN_BYTES = 1024
MAX_BYTES = 3*1024*1024
EXPIRATION= 60

def create_presigned_url(Audio_bucket, RequestID):
    s3_client = boto3.client('s3')


    fields = {
        "Content-Type": CONTENT_TYPE,
        "sucess_action_status": "201"
    }

    conditions = [
        {"Content-Type": CONTENT_TYPE},
        {"success_action_status": "201"}, #Return body with key
        ["content-length-range", MIN_BYTES, MAX_BYTES]
    ]

    try:
        fields = s3_client.generate_presigned_post(
            Bucket= audio_bucket,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=EXPIRATION,
            
        )
    except ClientError as e:
        logging.error(e)
        return None
    return fields

def lambda_handler(event, context):
    bucket_name = os.environ["BUCKET_NAME"]
    if not bucket_name:
        print("No bucket name found")
        exit(1)

    request_id = str(uuid.uuid4())
    key = f"uploads/{request_id}-audio"
    presigned_fields = create_presigned_url(Audio_bucket= bucket_name, requestID = request_id)

    if not presigned_fields:
        print("Presigned url generation failed")
        exit(1)

    result = {
        "requestId": request_id,
        "s3key": presigned_fields["url"],
        "fields": presigned_fields["fields"]
    }

    return json.dumps(result)