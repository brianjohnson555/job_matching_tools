# Job matching tools
My job search toolkit. This repository is used for three purposes:

1. Deploying web scrapers to scrape online job postings.
2. Finding top matches between job postings and my resume, to aid my job search. Also, to help identify keywords to better tailor my resume to a given job description.
3. Exploratory learning on using various models/methods to perform the resume/job matching in item (2), using an existing dataset of over 100k job postings downloaded from [Kaggle](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings/data).

[See my project blog for more details about this project](https://johnsonrobotics.com/Projects/jobsearch)

As this is a work in progress, I make no guarantees about the functionality of the code. Also note that web scraping of sites like LinkedIn can result in IP blocking; use the web scraping tools at your own risk.

# Web scrape overview
I use requests, fake-useragent, BeautifulSoup, and rotating residential proxies to scrape job postings from the web based on user query. The scraper extracts the job title, company, link to the posting, date posted, and job description (JD). User agents and proxies are deployed to avoid/prevent detection. There is also a filter that can be added to the query to automatically ignore postings from job aggregator services like Jobot or Jobs Via Dice, or to filter out specific job titles (for example, filter jobs titled "manager" or "lead").

# Job matching overview
Using the scraped JDs and the user's resume file, I employ a similarity ranking to identify top jobs where the JD best matches the resume. Cosine similarity is computed from embeddings generated from SBERT or FastText. I also employ a keyword identifier via Spacy NER to pick up matching keywords between the JD and resume (topics, skills, services). The user can add specific keywords to promote or demote the ranking of jobs in the results (for example, promote jobs that include the keyword "Python", demote jobs that include the keyword "Ph.D.").

# Deployment
Currently a work in progress, the web-scrape and job-match services are being deployed via Docker images to AWS cloud. The user can submit a query (job title, location, posted within X days, etc.) to a REST API, which passes the query to AWS Lambda to run the services. Results are returned via html and populated to a DynamoDB database for later use.
