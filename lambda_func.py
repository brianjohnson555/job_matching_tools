import json
import pandas as pd
from bs4 import BeautifulSoup
import src.job_scrape_funcs as scrape
import src.analysis as ana
import src.models as models

def job_pipeline(job_title, location, post_time, pages, resume_path, word_scores):
    print("Starting job scrape")
    job_data = scrape.scrape_jobs(pages=pages, job_title=job_title, location=location, post_time=post_time)
    raw_df = pd.DataFrame(job_data["jobs"])
    df = ana.find_job_match(models.embed_model, models.nlp_model, raw_df, resume_path, models.stop_words, word_scores)
    print("Generating report")
    html = ana.generate_html_report(df)
    return html

def lambda_handler(event, context):
    print("Raw event received:")
    print(json.dumps(event, indent=2))
    
    try:
        body = json.loads(event["body"])
        job_title = str(body.get("job title",""))
        location = str(body.get("location", "United States"))
        pages = int(body.get("pages", 1))
        word_scores = body.get("word scores", dict())
        post_time = float(body.get("post time", 0.25))
        print("Request received with body")
    except:
        job_title = str(event.get("job title",""))
        location = str(event.get("location", "United States"))
        pages = int(event.get("pages", 1))
        word_scores = event.get("word scores", dict())
        post_time = float(event.get("post time", 0.25))
        print("Request received without body")
        
    html = job_pipeline(job_title=job_title, 
                        location=location, 
                        post_time=post_time, 
                        pages=pages,
                        resume_path="data/resume.pdf",
                        word_scores=word_scores)
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html"
        },
        "body": html
    }