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
nlp = spacy.load("en_core_web_lg")
model = SentenceTransformer('all-MiniLM-L6-v2')
# ft = fasttext.load_model('./data/fasttext/cc.en.300.bin')

def cos_sim(a,b):
    """Cosine similarity between vectors a, b"""
    return dot(a, b)/(norm(a)*norm(b))

def find_job_match(job_data: pd.DataFrame, resume_path: str):
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

    # Calculate cos_sim and sort:
    df["similarity"] = df["embedding"].map(lambda a: cos_sim(a, b=resume_embed))
    df.sort_values(by=["similarity"], ascending=False, inplace=True)
    df = df[0:25].copy()# top 25 results
    df.reset_index(inplace=True, drop=True)

    # Calculate keywords between resume, job description:
    df["keywords"] = df["description"].map(lambda job_desc: find_keywords(job_desc, resume=resume))
    df.sort_values(by="keywords", key=lambda x: x.str.len(), ascending=False, inplace=True) # sort by highest number of matching keywords

    return df

def find_keywords(job_desc: str, resume: str):
    """Returns set of keywords based on NER via spacy pretrained."""
    job_desc = re.sub(r'[^\w\s]|[\d_]', '', job_desc) # remove punctuation
    resume = re.sub(r'[^\w\s]|[\d_]', '', resume) # remove punctuation
    res = nlp(resume)
    des = nlp(job_desc)

    remove_pos = ["ADV", "ADJ", "VERB"]
    custom_stop_words = {"team", "work", "tool", "system", "experience", "problem", " ", "  ", "Chicago", "IL"}
    # TODO: Chicago, IL are custom words based on my resume -- extend capability to all resumes, or ignore?

    resumeset = set([token.text for token in res 
                     if not token.is_stop # remove stop words
                     and token.pos_ not in remove_pos # remove adverbs, adjectives, verbs
                     and token.lemma_.lower() not in custom_stop_words]) # remove custom words
    jobset = set([token.text for token in des 
                  if not token.is_stop 
                  and token.pos_ not in remove_pos
                  and token.lemma_.lower() not in custom_stop_words])
    #TODO: also return fuzzy/close matches, e.g. Ph.D. <-> PhD
    return resumeset.intersection(jobset)

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
        print(f"{job_match_df["title"][result]}")
        print(f"{job_match_df["company"][result]}")
        print(f"{job_match_df["location"][result]}")
        print(f"{job_match_df["link"][result]}")
        print(f"Matching keywords: {job_match_df["keywords"][result]}")
        print(f"Description:\n\t {job_match_df["description"][result].replace("\n","\n\t")}") #indent description
        print("\n\n") # space before next result
