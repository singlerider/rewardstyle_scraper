# -*- coding: utf-8 -*-

# TODO A lot. force follow and scrape redirects
# Once I pass the redirect, I will scrape all advertisers pages and provide
# analytics with my existing analytics portion that runs at the end

from config import *
from lib.libs import *
from bs4 import BeautifulSoup # For HTML parsing
import urllib2 # Website connections
import re # Regular expressions
from time import sleep # To prevent overwhelming the server between connections
from nltk.corpus import stopwords # Filter out stopwords, such as "the", "or", "and"
import pandas as pd # For converting results to a dataframe and bar chart plots
import requests
import json

def rstyle_search(advertiser):
    url = "https://api.rewardstyle.com/v1/search?oauth_token={}&advertisers[]={}".format(access_token, advertiser)
    resp = requests.get(url)
    data = json.loads(resp.content)
    product_id = data["products"][0]["product_id"]
    return product_id


def rstyle_link(advertiser):
    try:
        rstyle_search(advertiser)
    except Exception as error:
        return error
    url = "https://api.rewardstyle.com/v1/get_link?oauth_token={}&product={}".format(access_token, rstyle_search(advertiser))
    resp = requests.get(url)
    data = json.loads(resp.content)
    link = data["link"]
    print "short link:", link
    return link


def text_cleaner(stripped_advertiser, website):
    soup_obj = BeautifulSoup(website, "html.parser")
    for script in soup_obj(["script", "style"]):
        script.extract() # Remove these two elements from the BS4 object
    text = soup_obj.get_text()
    with open('sites/{}.html'.format(stripped_advertiser.lower()), 'w') as f:
        f.write(soup_obj.encode("utf-8"))
    lines = (line.strip() for line in text.splitlines()) # break into lines
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    def chunk_space(chunk):
        chunk_out = chunk + " "
        return chunk_out
    text = "".join(chunk_space(chunk) for chunk in chunks if chunk).encode("utf-8")
    try:
        text = text.decode("unicode_escape").encode("ascii", "ignore")
    except Exception as error:
        return
    text = re.sub("[^a-zA-Z.+3]"," ", text)
    text = text.lower().split()
    stop_words = set(stopwords.words("english"))
    text = [w for w in text if not w in stop_words]
    text = list(set(text))
    return text


#sample = text_cleaner("http://www.indeed.com/viewjob?jk=5505e59f8e5a32a4&q=%22data+scientist%22&tk=19ftfgsmj19ti0l3&from=web&advn=1855944161169178&sjdu=QwrRXKrqZ3CNX5W-O9jEvWC1RT2wMYkGnZrqGdrncbKqQ7uwTLXzT1_ME9WQ4M-7om7mrHAlvyJT8cA_14IV5w&pub=pub-indeed")
#print sample[:20] # Just show the first 20 words

def scrape():
    successful_scrapes = 0
    for i in range(len(advertisers)):
        raw_advertiser = advertisers[i].encode("ascii", "xmlcharrefreplace").lower()
        print "advertiser raw:", raw_advertiser
        advertiser = raw_advertiser
        if "and" in advertiser:
            advertiser = advertiser.split("and")[0].strip(" ")
        if ".com" in advertiser:
            advertiser = advertiser.replace(".com", "")
        stripped_advertiser = advertiser.replace(" ", "_")
        advertiser = urllib2.quote(advertiser)
        print "advertiser (url safe):", advertiser
        print "Working on advertiser {} out of {} ({})".format(i + 1,
            len(advertisers), raw_advertiser)
        try:
            short_url = rstyle_link(advertiser)
            short_resp = requests.get(short_url)
            short_data = short_resp.content.encode("utf-8")
        except Exception as error:
            print "Error while scraping. No results found for advertiser"
            continue
        try:
            follow_on_url = re.search('<!-- (.*) -->', short_data).group(1)
            print "follow on url:", follow_on_url
            follow_on_resp = requests.get(follow_on_url)
            print "final follow on url:", follow_on_resp.url
            follow_on_data = str(follow_on_resp.content)
            text_cleaner(stripped_advertiser, follow_on_data.decode("utf-8"))
            print "advertiser {} scraped".format(i + 1)
            successful_scrapes += 1
        except Exception as error:
            print error

    print "Done with collecting the job postings!"
    print "There were", successful_scrapes, "scrapes performed successfully."

    #fashion_dict["Zipper"] = 3
    #fashion_dict["Wrinkle"] = 1
    intermediate_total_skills = fashion_dict
    #print intermediate_total_skills
    overall_total_skills = {}
    for key in intermediate_total_skills:
        if intermediate_total_skills[key] > 0:
            overall_total_skills[key] = intermediate_total_skills[key]

    final_frame = pd.DataFrame(overall_total_skills.items(), columns = ["Term", "NumPostings"])
    final_frame.NumPostings = (final_frame.NumPostings)*100/(len(advertisers))
    final_frame.sort_values(by= "NumPostings", ascending = False, inplace = True)

    return final_frame # End of the function
