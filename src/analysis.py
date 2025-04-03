from numpy import dot
from numpy.linalg import norm
import fasttext
import pandas as pd
import spacy
import pymupdf

# load pretrained data:
nlp = spacy.load("en_core_web_lg")
ft = fasttext.load_model('./data/fasttext/cc.en.300.bin')

def cos_sim(a,b):
    """Cosine similarity between vectors a, b"""
    return dot(a, b)/(norm(a)*norm(b))

def find_job_match(job_data: pd.DataFrame, resume_path: str):
    """Returns DataFrame of top matching jobs, based on:
    (1) cosine similarity between resume and job description embeddings
    (2) keyword match between resume and job description via NER"""

    df = job_data
    resume = parse_resume(resume_path)

    # Compute embeddings:
    df["embedding"] = df["description"].map(ft.get_word_vector)
    resume_embed = ft.get_word_vector(resume)

    # Calculate cos_sim and sort:
    df["similarity"] = df["embedding"].map(lambda a: cos_sim(a, b=resume_embed))
    df.sort_values(by=["similarity"], ascending=False)
    df = df[0:15].copy()# top 15 results

    # Calculate keywords between resume, job description:
    df["keywords"] = df["description"].map(lambda job_desc: find_keywords(job_desc, resume=resume))
    df.sort_values(by="keywords", key=lambda x: x.str.len(), ascending=False) # sort by highest number of matching keywords

    return df

def find_keywords(job_desc: str, resume: str):
    """Returns set of keywords based on NER via spacy pretrained."""
    res = nlp(resume)
    des = nlp(job_desc)

    resumeset = set([ent.text for ent in res.ents])
    jobset = set([ent.text for ent in des.ents])
    #TODO: also return fuzzy/close matches, e.g. Ph.D. <-> PhD
    return resumeset.intersection(jobset)

def parse_resume(resume_path: str):
    """Parses resume assuming pdf format."""
    doc = pymupdf.open(resume_path) # open a document
    text = ""
    for page in doc: # iterate the document pages
        text += page.get_text().replace("\n", " ") # get plain text encoded as UTF-8
    return text
