import json
import boto3

step = boto3.client('stepfunctions')

def lambda_handler(event, context):
    execution_arn = event["queryStringParameters"]["executionArn"]
    response = step.describe_execution(executionArn=execution_arn)

    return {
        "status": response["status"],
        "output": json.loads(response["output"]) if response["status"] == "SUCCEEDED" else None
    }