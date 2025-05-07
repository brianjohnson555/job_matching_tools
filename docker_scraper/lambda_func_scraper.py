"""Entry point for Lambda Function, running lambda_handler()"""
import json
from bs4 import BeautifulSoup
import job_scrape as scrape
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table('job-db')

def lambda_handler(event, context):
    print("Request received: \n", json.dumps(event))
    # Get input from event:
    try:
        body = json.loads(event["Payload"])
        url = str(body.get("url",""))
        query = str(body.get("query","").lower())
        print("Request received with body")
    except:
        url = str(event.get("url",""))
        query = str(event.get("query","").lower())
        print("Request received without body")
        
    # Scrape job data:
    job_data = scrape.scrape_job_single(url, query)
    
    if not job_data: # if initial call had an error, retry
        job_data = scrape.scrape_job_single(url, query) # try again
    
    if job_data:
        response = table.put_item(Item=job_data) # write data to table
        print("DynamoDB put_item response:", response)
    else:
        print("Failed job scraping, no data sent to DynamoDB")