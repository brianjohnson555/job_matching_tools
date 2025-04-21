import json
import pandas as pd
import analysis as ana
import models as models
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table('YourTableName')

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        word_scores = body.get("word scores", dict())
        post_time = float(body.get("post time", 0.25))
        print("Request received with body")
    except:
        word_scores = event.get("word scores", dict())
        post_time = float(event.get("post time", 0.25))
        print("Request received without body")
    
    print("Getting data from DynamoDB")
    raw_df = pd.DataFrame(table)
    print("Finding matches")
    df = ana.find_job_match(models.embed_model, models.nlp_model, raw_df, "data/resume.pdf", models.stop_words, word_scores)
    print("Generating report")
    html = ana.generate_html_report(df)
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html"
        },
        "body": html
    }