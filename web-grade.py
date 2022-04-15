# To run this, download the BeautifulSoup zip file
# http://www.py4e.com/code3/bs4.zip
# and unzip it in the same directory as this file

# The program will use urllib to read the HTML from the data files below,
# extract the href= values from the anchor tags,
# scan for a tag that is in a particular position relative to the
# first name in the list, follow that link and repeat the process
# a number of times and report the last name you find.

import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
import re

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Get list of URL on webpage
def linkSearch(url):
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')
    urllist = []
    # Retrieve all of the anchor tags, make a list of urls
    tags = soup('a')
    urllist.append(url)
    for tag in tags:
        content = tag.get('href', None)
        urllist.append(content)
    #print(urllist)
    return urllist

# Get the nTH URL in a list of URLs
def nextUrl(urllist, n):
    nexturl = str(urllist[n])
    #print(nexturl)
    return nexturl

# Find the name after the word by, in a URL
def nameSearch(nexturl):
    fr = [re.findall('by_([^.]*)', s) for s in nexturl]
    #print(fr)
    return fr

def findurllist(url):
    urlNames = []
    for u in range(7):
            ulist1 = linkSearch(url)
            findurl = nextUrl(ulist1, 18)
            urlNames.append(findurl)
            url = findurl
    return urlNames


#newurllist = findurllist('http://py4e-data.dr-chuck.net/known_by_Ada.html')
#names = nameSearch(newurllist)
names = linkSearch('https://codeprojects.org/i15phTNxxb1YRG8VXVy6HFfVxT58uEmdFlkM55vc-ck/')
print(names)
