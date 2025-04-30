import json
import pandas as pd
import analysis as ana
import models as models
import io
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta, timezone

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table('job-db')
s3 = boto3.client('s3')
bucket_name = 'job-tools'
object_key = 'uploads/resume.pdf'
# Get PDF from S3
print("Setting up resume file")
response = s3.get_object(Bucket=bucket_name, Key=object_key)
pdf_bytes = response['Body'].read()
pdf_file_like = io.BytesIO(pdf_bytes)

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        word_scores = body.get("word scores", dict())
        query = str(body.get("query",""))
        post_time = float(body.get("post time", 1))
        print("Request received with body")
    except:
        word_scores = event.get("word scores", dict())
        query = str(event.get("query","")).lower()
        post_time_days = float(event.get("post time", 1))
        post_time = (datetime.now(timezone.utc) - timedelta(days=post_time_days)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        print("Request received without body")
    
    print("Getting data from DynamoDB")
    
    response = table.query(KeyConditionExpression=Key('query').eq(query) & Key('date').gt(post_time))
    items = response['Items']

    expected_keys = ["query", "date", "title", "company", "description", "location", "link"]
    raw_df = pd.DataFrame.from_records(items, columns=expected_keys)
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