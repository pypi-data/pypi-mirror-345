import json

import boto3

from common_utils.constants import INVOCATION_AND_ERROR_LOGGING_URL


def send_invocation_or_error_message(message):
    session = boto3.session.Session()
    sqs_client = session.client(service_name="sqs")
    if not message:
        return False
    try:
        message = json.dumps(message, default=str)
        sqs_client.send_message(QueueUrl=INVOCATION_AND_ERROR_LOGGING_URL, MessageBody=message)
        return True
    except Exception as error:
        print(f"ERROR: function: send_invocation_or_error_message {error}")
        return False
