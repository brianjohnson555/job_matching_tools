import json
import pandas as pd
import src.job_scrape_funcs as scrape
import src.analysis as ana

def job_pipeline(job_title, location, post_time, pages, resume_path):
    print("Starting job scrape")
    job_data = scrape.scrape_jobs(pages=pages, job_title=job_title, location=location, post_time=post_time)
    raw_df = pd.DataFrame(job_data["jobs"])
    df = ana.find_job_match(raw_df, resume_path)
    print("Generating report:\n\n")
    ana.generate_report(df)
    return df

job_pipeline(job_title="Data Scientist", 
                  location="Chicago", 
                  post_time=0.26, 
                  pages=5,
                  resume_path="resume.pdf")