"""Entry point for Lambda Function, running lambda_handler()"""
import json
import sys
import traceback
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


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print("JSON input not supplied. Expected command: python lambda_func_scraper '<json_input>'", flush=True)
            sys.exit(1)

        event = json.loads(sys.argv[1])
        context = {}  # Simulate empty Lambda context
        lambda_handler(event, context)
        print("Successful task_scraper execution.", flush=True)
    except Exception as e:
        print(e)
        print("[ERROR] Exception occurred:", file=sys.stderr, flush=True)
        traceback.print_exc()
        sys.exit(1)