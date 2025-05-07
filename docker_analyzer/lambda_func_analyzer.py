"""Entry point for Lambda function via lambda_handler()"""
import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta, timezone


REQUIRED_KEYS = ["query", "word_scores", "post_time"]

# Verify input content has all required keys:
def validate_input(event):
    missing = [key for key in REQUIRED_KEYS if key not in event]
    if missing:
        raise ValueError(f"Missing required keys: {missing}")

def lambda_handler(event, context):
    try:
        validate_input(event)
        word_scores = event.get("word_scores", dict())
        query = str(event.get("query","")).lower()
        post_time_days = float(event.get("post_time", 1))
        post_time = (datetime.now(timezone.utc) - timedelta(days=post_time_days)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    except Exception as e:
        print("Error with query format")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"Error": str(e)})
            }
    
    # Query DynamoDB table to obtain scraped results:
    print("Getting data from DynamoDB")
    import pandas as pd
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table('job-db')
    response = table.query(KeyConditionExpression=Key('query').eq(query) & Key('date').gt(post_time))
    items = response['Items']
    
    # Verify format and add None if key not available:
    expected_keys = ["query", "date", "title", "company", "description", "location", "link"]
    items_normalized = [{key: item.get(key, None) for key in expected_keys} for item in items]
    raw_df = pd.DataFrame(items_normalized)

    # Check if query returned empty dataset:
    if len(raw_df.index) == 0:
        print("Error, query returne empty database")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": "Query returned empty database. Modify query or post_time."})
            }
    
    # Get PDF from S3
    print("Setting up resume file")
    object_key = 'uploads/resume.pdf'
    bucket_name = 'job-tools'
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    pdf_bytes = response['Body'].read()
    import io
    pdf_file_like = io.BytesIO(pdf_bytes)

    # importing analysis and model files
    import analysis as ana
    import models as models

    print("Finding matches")
    df = ana.find_job_match(models.embed_model, models.nlp_model, raw_df, pdf_file_like, models.stop_words, word_scores)
    print("Generating report")
    html = ana.generate_html_report(df)
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html"
        },
        "body": html
        }