
# The program will use urllib to read the HTML from a URL,
# extract tags and frequency used, extract links and broken links


import ssl
import socket
import urllib.error
import urllib.parse
import urllib.request
import requests
from bs4 import BeautifulSoup

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


# Retrieve tags frequency, using urlopen()
def get_tags(url):
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')
    tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'img']
    results = {}
    for tag in tags:
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
    for ele in data:
        if 'class' in ele:
            print(ele)


# check for broken links
def link_status(url):
    page = requests.get(url)
    response_code = str(page.status_code)
    data = page.text
    soup = BeautifulSoup(data, 'lxml')
    for link in soup.find_all('a'):
        status = "URL: {} | Status: {}".format(link.get('href'), response_code)
        return status


# Get list of URL on webpage
def get_links(url):
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'lxml')
    urllist = []
    # Retrieve anchor tags, make a list of urls
    tags = soup('a')
    urllist.append(url)
    for tag in tags:
        content = tag.get('href', None)
        urllist.append(content)
    return urllist


def check_localhost():
    localhost = socket.gethostbyname('localhost')
    return localhost == '127.0.0.1'


# Check url connectivity
def check_connectivity(url):
    request = requests.get(url)
    response_code = request.status_code
    return response_code == 200


# Create HTML page with results
def html_output(feedback):
    with open('MST.html', 'w') as html_pg:
        html_pg.write('<html>\n<head>\n<title> \n Teacher Feedback for Web Project \
           </title>\n</head> <body><h1>Your Results for the<u>Web Page Project</u></h1>\
           \n<h2>A <u>CS</u> {} </h2> \n</body></html>'.format(feedback))

html_output("good job")