"""Script to call AWS API for job scrape task. Requires key.txt which is untracked in this repository
for API privacy reasons.

Usage: modify variable "data" to change user query, then simply run the script. 
Output will write to "output.html", viewable from any browser. """

import requests
import json
import time
from bs4 import BeautifulSoup

data =  json.dumps({
    "query": "Data Scientist",
    "location": "Chicago",
    "pages": 100,
    "post_time": 4,
    "word_scores": {
        "phd": 1.1,
        "python": 1.1,
        "senior": 0.8
        }
})

with open("key.txt", "r") as f:
    api_key = str(f.read()) # retrieve AWS API key from file

url = "https://uztyzxzel0.execute-api.us-east-1.amazonaws.com/job-api-stage1/jobscrape"

headers = {
    "Content-Type": "application/json",
    "x-api-key": api_key
}

response = requests.post(url, data=data, headers=headers) # make initial POST to API gateway

if response.status_code != 202:
    print("Request failed with response code ", response.status_code)
    print(response.text)

executionArn = str(response.json()["executionArn"]) # retrieve executionARN from API response
print(executionArn)
time.sleep(5) # let step function initialize


payload = json.dumps({
  "executionArn": executionArn
})
going = True
retries = 0

while going:
    response = requests.get(url=url, data=payload, headers=headers) # make GET polling request to API gateway
    if response.status_code != 200:
        print("Error with GET request.")
        print(response.text)
        # Sometimes API returns error even though step function continues successful execution.
        # This enables some retries of the GET request:
        time.sleep(60)
        retries += 1
        if retries > 3:
            print("Retries exceeded, stopping.")
            break
    elif response.json()["status"]=="RUNNING":
        print("Running...")
        time.sleep(30) # wait before polling again
    elif response.json()["status"]=="FAILED" or response.json()["status"]=="TIMED_OUT":
        print("Step function failed, check CloudWatch logs")
    elif response.json()["status"]=="SUCCEEDED":
        going = False
        html = response.json()["output"]["Payload"]["body"] # get ranked jobs from API response
        soup = BeautifulSoup(html, features="html.parser") # parse to html

        with open("output.html", "w", encoding="utf-8") as file:
            file.write(str(soup)) # write html to file
        print("Finished!")
    

