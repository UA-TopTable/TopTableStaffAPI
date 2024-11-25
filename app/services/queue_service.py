import os
import boto3


def get_reservation_confirmation(restaurant_id_list,sqs=boto3.client('sqs'),queue_url=os.getenv("SQS_RESERVATION_RESQUESTS_QUEUE_URL")):
    while True:
        response=sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=30
        )
        if "Messages" in response:
            for message in response["Messages"]:
                if int(message["MessageAttributes"]["restaurant_id"]["StringValue"]) in restaurant_id_list:
                    return message


def delete_reservation_confirmation(message,sqs=boto3.client('sqs'),queue_url=os.getenv("QUEUE_URL")):
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=message["ReceiptHandle"]
    )