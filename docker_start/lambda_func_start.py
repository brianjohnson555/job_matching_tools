import json
import boto3
import uuid

step = boto3.client('stepfunctions')

def lambda_handler(event, context):
    request_id = str(uuid.uuid4())
    input_payload = {
        "query": str(event.get("query","")),
        "location": str(event.get("location", "United States")),
        "pages": int(event.get("pages", 10)),
        "post_time": float(event.get("post_time", 1)),
    }

    execution = step.start_execution(
        stateMachineArn="arn:aws:states:us-east-1:711387109035:stateMachine:job-scrape-machine",
        name=request_id,
        input=json.dumps(input_payload)
    )

    return {
        "statusCode": 202,
        "body": json.dumps({"request_id": request_id,
                "executionArn": execution["executionArn"]
        })
    }