import json
import boto3
import uuid

step = boto3.client('stepfunctions')

REQUIRED_KEYS = ["query", "location", "pages", "post_time", "word_scores"]

def validate_input(body):
    missing = [key for key in REQUIRED_KEYS if key not in body]
    if missing:
        raise ValueError(f"Missing required keys: {missing}")

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"]) if "body" in event else event
        validate_input(body)
        request_id = str(uuid.uuid4())
        # format input
        input_payload = {
            "query": str(body.get("query","")),
            "location": str(body.get("location", "United States")),
            "pages": int(body.get("pages", 10)),
            "post_time": float(body.get("post_time", 1)),
            "word_scores": body.get("word_scores", dict()),
        }

        # start AWS step function execution
        execution = step.start_execution(
            stateMachineArn="arn:aws:states:us-east-1:711387109035:stateMachine:job-scrape-machine",
            name=request_id,
            input=json.dumps(input_payload)
        )
    except (ValueError, json.JSONDecodeError) as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }

    return {
        "statusCode": 202,
        "body": json.dumps({"request_id": request_id,
                "executionArn": execution["executionArn"]
        })
    }