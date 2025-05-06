"""Script to call AWS API for job scrape task. Requires key.txt which is untracked in this repository
for API privacy reasons.

Usage: modify variable data to change user query, then simply run the script. Output will write to output.html"""

import requests
import json
import time
from bs4 import BeautifulSoup

data =  json.dumps({
    "query": "Research Scientist",
    "location": "Chicago",
    "pages": 80,
    "post_time": 2,
    "word_scores": {
        "phd": 1.1,
        "python": 1.1,
        "senior": 0.8
        }
})

with open("key.txt", "r") as f:
    api_key = str(f.read())

url = "https://uztyzxzel0.execute-api.us-east-1.amazonaws.com/job-api-stage1/jobscrape"

headers = {
    "Content-Type": "application/json",
    "x-api-key": api_key
}

response = requests.post(url, data=data, headers=headers)

if response.status_code != 202:
    print("Request failed with response code ", response.status_code)
    print(response.text)

executionArn = str(response.json()["executionArn"])
print(executionArn)

payload = json.dumps({
  "executionArn": executionArn
})

time.sleep(5)
going = True
retries = 0

while going:
    response = requests.request("GET", url=url, data=payload, headers=headers)
    if response.status_code != 200:
        print("Error with GET request.")
        print(response.text)
        time.sleep(15)
        retries += 1
        if retries > 3:
            print("Retries exceeded, stopping.")
            break
    if response.json()["status"]=="RUNNING":
        print("Running...")
        time.sleep(30)
    elif response.json()["status"]=="FAILED" or response.json()["status"]=="TIMED_OUT":
        print("Step function failed, check CloudWatch logs")
    elif response.json()["status"]=="SUCCEEDED":
        going = False
        html = response.json()["output"]["Payload"]["body"]
        soup = BeautifulSoup(html, features="html.parser")

        with open("output.html", "w", encoding="utf-8") as file:
            file.write(str(soup))
        print("Finished!")
    

