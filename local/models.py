"""Sets models and custom stop word list for analysis functions in analysis.py."""
import spacy
nlp_model = spacy.load("en_core_web_sm") #sm, md, lg

### If using fastText:
# import fasttext
# ft = fasttext.load_model('./data/fasttext/cc.en.300.bin')

### If using SBERT:
from sentence_transformers import SentenceTransformer
# embed_model = SentenceTransformer('all-MiniLM-L6-v2')
embed_model = SentenceTransformer('/models/sbert')

# custom stop words:
stop_words = {"team", "work", "tool", "system", "experience", "problem", " ", "  ", "product", 
                     "university", "degree", "fund", "member", "content"}

# add city and country names to stop words:
with open("./docker_analyzer/data/cities1000.txt", encoding="utf-8") as f:
    cities = set(line.split("\t")[1].lower() for line in f)
with open("./docker_analyzer/data/countries.txt", encoding="utf-8") as f:
    countries = set(line.split("\t")[1].lower() for line in f)
stop_words.update(set(cities)) # add city names to stop words
stop_words.update(set(countries)) # add country names to stop words