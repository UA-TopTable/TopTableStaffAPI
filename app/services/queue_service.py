import json
import os
import sys
import boto3


def get_reservation_confirmation(restaurant_id_list,sqs=boto3.client('sqs', region_name='us-east-1'),queue_url=os.getenv("SQS_RESERVATION_RESQUESTS_QUEUE_URL")):
    while True:
        response=sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
        )
        print(f"received on sqs: {response}",file=sys.stderr)
        if "Messages" in response:
            for message in response["Messages"]:
                body=message["Body"]
                body=json.loads(body.replace("'",'"'))
                print(f"request restaurant id: {body['reservation']['restaurant_id']}",file=sys.stderr)
                if "reservation" in body and int(body["reservation"]["restaurant_id"]) in restaurant_id_list:
                    return message


def delete_reservation_confirmation(receipt_handle,sqs=boto3.client('sqs', region_name='us-east-1'),queue_url=os.getenv("QUEUE_URL")):
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )