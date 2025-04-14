from numpy import dot
from numpy.linalg import norm
# import fasttext
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import spacy
import pymupdf
import re
from sentence_transformers import SentenceTransformer

# load pretrained data:
nlp = spacy.load("en_core_web_sm") #sm, md, lg
# model = SentenceTransformer('all-MiniLM-L6-v2')
model = SentenceTransformer('/models/sbert')
# ft = fasttext.load_model('./data/fasttext/cc.en.300.bin')
custom_stop_words = {"team", "work", "tool", "system", "experience", "problem", " ", "  ", "product", 
                     "university", "degree", "fund", "member", "content"}

def cos_sim(a,b):
    """Cosine similarity between vectors a, b"""
    return dot(a, b)/(norm(a)*norm(b))

def find_job_match(job_data: pd.DataFrame, resume_path: str, word_scores: dict):
    """Returns DataFrame of top matching jobs, based on:
    (1) cosine similarity between resume and job description embeddings
    (2) keyword match between resume and job description via NER"""

    resume = parse_resume(resume_path)

    # Compute embeddings:
    df = job_data[job_data["description"].isnull()==False] # remove any null values
    df["embedding"] = df["description"].map(lambda x: model.encode(x))
    # df["embedding"] = df["description"].map(ft.get_word_vector)
    # resume_embed = ft.get_word_vector(resume)
    resume_embed = model.encode(resume, convert_to_tensor=True)

    # Calculate keywords between resume, job description:
    df["keywords"] = df["description"].map(lambda job_desc: find_keywords(job_desc, resume=resume))
    # Calculate cos_sim:
    df["similarity"] = df["embedding"].map(lambda a: cos_sim(a, b=resume_embed))
    # Modify score based on keywords:
    #TODO: score all keywords, not just overlapping w/ resume.
    df["similarity_adj"] = df.apply(lambda row: score_keywords(row, word_scores=word_scores), axis=1)
    # Sort:
    df.sort_values(by=["similarity_adj"], ascending=False, inplace=True)
    df = df[0:25].copy()# top 25 results
    df.reset_index(inplace=True, drop=True)
    # df.sort_values(by="keywords", key=lambda x: x.str.len(), ascending=False, inplace=True) # sort by highest number of matching keywords

    return df

def find_keywords(job_desc: str, resume: str):
    """Returns set of keywords based on NER via spacy pretrained."""
    job_desc = re.sub(r'[^\w\s]|[\d_]', '', job_desc) # remove punctuation
    resume = re.sub(r'[^\w\s]|[\d_]', '', resume) # remove punctuation
    res = nlp(resume)
    des = nlp(job_desc)

    remove_pos = ["ADV", "ADJ", "VERB"]
    with open("./data/cities1000.txt", encoding="utf-8") as f:
        cities = set(line.split("\t")[1].lower() for line in f)
    with open("./data/countries.txt", encoding="utf-8") as f:
        countries = set(line.split("\t")[1].lower() for line in f)

    custom_stop_words.update(set(cities)) # add city names to stop words
    custom_stop_words.update(set(countries)) # add country names to stop words

    resumeset = set([token.text for token in res 
                     if not token.is_stop # remove stop words
                     and token.pos_ not in remove_pos # remove adverbs, adjectives, verbs
                     and token.lemma_.lower() not in custom_stop_words]) # remove custom words
    jobset = set([token.text for token in des 
                  if not token.is_stop 
                  and token.pos_ not in remove_pos
                  and token.lemma_.lower() not in custom_stop_words])
    #TODO: also return fuzzy/close matches
    return resumeset.intersection(jobset)

def score_keywords(row, word_scores):
    """Modifies similarity score based on presence of certain keywords"""
    sim = row["similarity"]
    for kw in row["keywords"]:
        if kw in word_scores:
            sim *= word_scores[kw]
    return sim

def parse_resume(resume_path: str):
    """Parses resume assuming pdf format."""
    doc = pymupdf.open(resume_path) # open a document
    text = ""
    for page in doc: # iterate the document pages
        text += page.get_text().replace("\n", " ") # get plain text encoded as UTF-8
    return text

def generate_report(job_match_df: pd.DataFrame):
    """Prints a generated report based on job match output."""
    for result in job_match_df.index[:10]: # retrieve top 10 results
        print(f"{job_match_df["title"][result]}, adj_score={job_match_df["similarity_adj"][result]:.2f}, orig_score={job_match_df["similarity"][result]:.2f}")
        print(f"{job_match_df["company"][result]}")
        print(f"{job_match_df["location"][result]}")
        print(f"{job_match_df["link"][result]}")
        print(f"Matching keywords: {job_match_df["keywords"][result]}")
        print(f"Description:\n\t {job_match_df["description"][result].replace("\n","\n\t")}") #indent description
        print("\n\n") # space before next result

def generate_html_report(job_match_df: pd.DataFrame) -> str:
    """Generates an HTML-styled report based on job match output."""
    html = """
    <html>
    <head>
        <style>
            body {font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; background-color: #f5f5f5;}
            .job-card {background: white; border-radius: 10px; padding: 15px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);}
            .job-title {font-size: 18px; font-weight: bold;}
            .company-location {font-size: 16px; color: #666;}
            .keywords {font-style: italic; margin-top: 10px;}
            .description {margin-top: 0; white-space: pre-wrap;}
            .description ul {margin-top: 0;}
            a {color: #1a0dab; text-decoration: none;}
            a:hover {text-decoration: underline;}
        </style>
    </head>
    <body>
        <h2>Top Job Matches</h2>
    """
    idx = 0
    for result in job_match_df.index[:10]:  # top 10 results
        idx += 1
        html += f"""
        <div class="job-card">
            <div class="job-title">#{idx} {job_match_df["title"][result]} — Score: {job_match_df["similarity_adj"][result]:.2f} (Raw: {job_match_df["similarity"][result]:.2f})</div>
            <div class="company-location">{job_match_df["company"][result]} | {job_match_df["location"][result]}</div>
            <div><a href="{job_match_df["link"][result]}" style="font-weight: bold;" target="_blank">View Job Posting</a></div>
            <div class="keywords">Keywords: {job_match_df["keywords"][result]}</div>
            <div class="description">
                <ul>
                    {''.join(f'<li>{line.strip()}</li>' for line in job_match_df["description"][result].splitlines() if line.strip())}
                </ul>
            </div>
        </div>
        """

    html += "</body></html>"
    return html
