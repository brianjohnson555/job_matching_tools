import json
import pandas as pd
import src.job_scrape_funcs as scrape
import src.analysis as ana
from datetime import datetime
from pathlib import Path

def job_pipeline(job_title, location, post_time, pages, resume_path):
    #TODO: try except statements
    # Scrape jobs:
    print("Starting job scrape")
    job_data = scrape.scrape_jobs(pages=pages, job_title=job_title, location=location, post_time=post_time)
    # date = datetime.today().strftime("%Y-%m-%d")

    # # Save:
    # index = 1
    # full_path = save_path+str(job_title).replace(" ","-")+"_"+str(date)+"_"+str(index)+".json"
    # while (Path.cwd()/full_path).exists():
    #     index += 1
    #     full_path = save_path+str(job_title).replace(" ","-")+"_"+str(date)+"_"+str(index)+".json"

    # print("Saving to ", full_path)
    # with open(full_path, 'w', encoding='utf-8') as f:
    #     json.dump(job_data, f, ensure_ascii=False, indent=4)

    # Find matches:
    # with open(full_path, 'r', encoding="utf-8") as f:
    #     data = json.load(f)

    raw_df = pd.DataFrame(job_data["jobs"])
    df = ana.find_job_match(raw_df, resume_path)
    print("Generating report:\n\n")
    ana.generate_report(df)
    return df

def lambda_handler(event, context):
    job_pipeline(job_title="Data Scientist", 
                  location="Chicago", 
                  post_time=0.26, 
                  pages=5,
                  resume_path="resume.pdf")    
    return {
        'statusCode': 200,
        'body': json.dumps('Scraping complete')
    }