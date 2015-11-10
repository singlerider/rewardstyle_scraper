import requests
import json
from bs4 import BeautifulSoup
import re

url = "http://rstyle.me/~qw-6RQWw"
resp = requests.get(url, allow_redirects=True)
print resp.url
#resp = requests.get(url)
data = resp.content
soup_obj = BeautifulSoup(data, "html.parser")
text = soup_obj.get_text() # Get the text from this
print text
lines = (line.strip() for line in text.splitlines()) # break into lines
chunks = (phrase.strip() for line in lines for phrase in line.split("  ")) # break multi-headlines into a line each
def chunk_space(chunk):
    chunk_out = chunk + ' ' # Need to fix spacing issue
    return chunk_out
text = ''.join(chunk_space(chunk) for chunk in chunks if chunk).encode('utf-8') # Get rid of all blank lines and ends of line
print type(text)
result = re.search('add(.*)er', text)
print result.group(1)
