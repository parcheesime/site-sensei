
# This code uses urllib to read the HTML from a URL,
# extract tags and frequency used, extract links and broken links


import ssl
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
import requests
from bs4 import BeautifulSoup

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


# Retrieve tags frequency dictionary, according to list of tags
def get_tags(url, tag_list):
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')
    results = {}
    for tag in tag_list:
        t = soup(tag)
        if tag not in soup(tag):
            results[tag] = 0
        results[tag] += len(t)
    return results


# Check for CSS clss selectors, using requests.get
def get_class(url):
    page = requests.get(url)
    data = page.text
    data = data.split()
    count_class = [ele for ele in data if 'class' in ele]
    return "CSS UPDATE: <br> Class attribute is used {} time(s).".format(len(count_class))


# Get list of URL on webpage
def get_links(url):
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')
    # Retrieve anchor tags, make a list of urls
    tags = soup('a')
    urllist = [tag.get('href', None) for tag in tags]
    return urllist


# Create HTML page with message displayed
def html_output(feedback):
    with open('MST.html', 'w') as html_pg:
        html_pg.write("<!DOCTYPE html><html>\n<head>\n<title> \n Teacher Feedback for Web Project \
           </title>\n</head> <body><h1>Your Results for the Web Page Project</h1>\
           \n<ul> {} </ul> \n</body></html>".format(feedback))
        return webbrowser.open('MST.html')
