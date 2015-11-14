# -*- coding: utf-8 -*-

from config import *
from lib.libs import *
from bs4 import BeautifulSoup  # For HTML parsing
import urllib2  # Website connections
import re  # Regular expressions
from time import sleep  # To prevent overwhelming the server
from nltk.corpus import stopwords  # Filter out stopwords, such as "the"
import pandas as pd  # For converting results to a dataframe
import requests
import json


def rstyle_search(advertiser):  # do a search for a given advertiser
    url = "https://api.rewardstyle.com/v1/search?oauth_token={}\
&advertisers[]={}".format(
        access_token, advertiser)
    resp = requests.get(url)
    data = json.loads(resp.content)  # if there is a result, grab the json
    product_id = data["products"][0]["product_id"]  # snag the top result
    return product_id


def rstyle_link(advertiser):  # gets a shortlink
    try:
        rstyle_search(advertiser)
    except Exception as error:
        return error
    url = "https://api.rewardstyle.com/v1/get_link?oauth_token={}\
&product={}".format(
        access_token, rstyle_search(advertiser))
    resp = requests.get(url)
    data = json.loads(resp.content)  # this is the json for the link request
    link = data["link"]  # snag the shortlink
    print "short link:", link
    return link


def text_cleaner(stripped_advertiser, website):  # clean up html and read words
    soup_obj = BeautifulSoup(website, "html.parser")
    for script in soup_obj(["script", "style"]):  # get rid of that nasty
        # javascript
        script.extract()  # Remove these two elements from the BS4 object
    text = soup_obj.get_text().replace(".", "")  # we convert text in place
    # several times coming up
    with open('sites/{}.html'.format(stripped_advertiser.lower()), 'w') as f:
        f.write(soup_obj.encode("utf-8"))  # write html out to file
    lines = (line.strip() for line in text.splitlines())  # break into lines
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

    def chunk_space(chunk):  # individual utf-8 encoded word chunks
        chunk_out = chunk + " "
        return chunk_out
    text = "".join(chunk_space(chunk) for chunk in chunks if chunk).encode(
        "utf-8")
    try:
        text = text.decode("unicode_escape").encode("ascii", "ignore")
    except Exception as error:
        return  # just in case there are some weird characters here, don't kill
    text = re.sub("[^a-zA-Z.+3]", " ", text)  # only regular words, no numbers
    text = text.lower().split()  # lower case so the dict can be populated
    stop_words = set(stopwords.words("english"))
    text = [w for w in text if w not in stop_words]  # gets rid of stop words
    text = list(set(text))  # no repeats!
    for word in text:
        if word not in fashion_dict:
            fashion_dict[word] = 1  # populate fashion dict
        else:
            fashion_dict[word] += 1  # increment entry
    return text


def scrape():
    successful_scrapes = 0  # keep track of scrapes that went through
    for i in range(len(advertisers)):  # per advertiser
        raw_advertiser = advertisers[i].encode(
            "ascii", "xmlcharrefreplace").lower()
        print "advertiser raw:", raw_advertiser
        advertiser = raw_advertiser
        if "and" in advertiser:
            advertiser = advertiser.split(
                "and")[0].strip(" ")  # separate multiple
            # advertisers and search for only the first listed
        if ".com" in advertiser:
            advertiser = advertiser.replace(
                ".com", "")  # could prevent search result
        # get rid of spaces for file name
        stripped_advertiser = advertiser.replace(" ", "_")
        advertiser = urllib2.quote(advertiser)  # url safe version
        print "advertiser (url safe):", advertiser
        print "Working on advertiser {} out of {} ({})".format(
            i + 1, len(advertisers), raw_advertiser)
        try:
            short_url = rstyle_link(advertiser)  # get shortlink
            short_resp = requests.get(short_url)
            short_data = short_resp.content.encode("utf-8")  # generate unicode
        except Exception as error:
            print "Error while scraping. No results found for advertiser"
            continue  # nothing else to do without the result
        try:
            follow_on_url = re.search('<!-- (.*) -->', short_data).group(1)
            print "follow on url:", follow_on_url
            follow_on_resp = requests.get(follow_on_url)
            print "final follow on url:", follow_on_resp.url
            follow_on_data = str(follow_on_resp.content)  # final html
            text_cleaner(stripped_advertiser, follow_on_data.decode("utf-8"))
            print "advertiser {} scraped".format(i + 1)
            successful_scrapes += 1  # great work - scrape successful
        except Exception as error:
            print error

    print "Done with collecting the job postings!"
    print "There were", successful_scrapes, "scrapes performed successfully."

    intermediate_total_skills = fashion_dict
    overall_total_skills = {}
    for key in intermediate_total_skills:
        if intermediate_total_skills[key] > 0:
            overall_total_skills[key] = intermediate_total_skills[key]

    final_frame = pd.DataFrame(overall_total_skills.items(), columns=[
        "Term", "NumPostings"])
    pd.set_option('display.height', 500000)  # this is just an arbitrary max
    pd.set_option('display.max_rows', 500000)
    final_frame.NumPostings = (
        (final_frame.NumPostings)*100)/successful_scrapes
    final_frame.sort_values(by="NumPostings", ascending=False, inplace=True)
    import time
    with open('sites/word_freq_{}.txt'.format(int(time.time())), 'w') as f:
        f.write(str(final_frame))  # why not write out the analytics to file?

    return final_frame  # End of the function
