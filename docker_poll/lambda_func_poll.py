"""Entry point for polling Lambda Function"""
import json
import boto3

step = boto3.client('stepfunctions')

def lambda_handler(event, context):
    print("Request received")
    # get input from event:
    body = json.loads(event["body"])
    execution_arn = body.get("executionArn")
    response = step.describe_execution(executionArn=execution_arn)

    # return current status:
    return {
    "statusCode": 200,
    "headers": { "Content-Type": "application/json" },
    "body": json.dumps({
        "status": response["status"],
        "output": json.loads(response["output"]) if response["status"] == "SUCCEEDED" else None
    })
    }