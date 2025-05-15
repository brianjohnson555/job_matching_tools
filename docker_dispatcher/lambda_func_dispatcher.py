"""Entry point for Lambda Function"""
import sys
import json
from bs4 import BeautifulSoup
import url_scrape as scrape
import traceback

def lambda_handler(event, context):
    # get input query from event:
    print(json.dumps(event))
    job_title = str(event.get("query",""))
    location = str(event.get("location", "United States"))
    pages = int(event.get("pages", 1))
    post_time = float(event.get("post_time", 0.5))

    # Scrape job urls from main results page:
    print("Starting job URL scrape")
    urls = scrape.scrape_job_urls(pages=pages, job_title=job_title, location=location, post_time=post_time)
    # Return urls for map state:
    return {
            "url_list": urls,
            "query": job_title
            }

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print("JSON input not supplied. Expected command: python lambda_func_dispatcher '<json_input>'", flush=True)
            sys.exit(1)

        event = json.loads(sys.argv[1])
        context = {}  # Simulate empty Lambda context
        result = lambda_handler(event, context)
        print(json.dumps(result), flush=True)
    except Exception as e:
        print(e)
        print("[ERROR] Exception occurred:", file=sys.stderr, flush=True)
        traceback.print_exc()
        sys.exit(1)