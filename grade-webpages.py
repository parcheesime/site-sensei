
# The program will use urllib to read the HTML from a URL,
# extract tags and frequency used, extract links and broken links


import ssl\

import requests
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


# Retrieve tags frequency
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


def get_class(url):
    page = requests.get(url)
    data = page.text
    data = data.split()
    for ele in data:
        if 'class' in ele:
            print(ele)


def get_soup(url):
    html = urllib.request.urlopen(url, context=ctx).read()
    soup1 = BeautifulSoup(html, 'html.parser')
    print(soup1)
    page = requests.get(url)
    data = page.text
    soup2 = BeautifulSoup(data, 'lxml')
    print(soup2)


def check_localhost():
    localhost = socket.gethostbyname('localhost')
    return localhost == '127.0.0.1'


def check_connectivity():
    request = requests.get("http://www.google.com")
    response_code = (request.status_code)
    return response_code == 200

print(check_localhost())
print(check_connectivity())