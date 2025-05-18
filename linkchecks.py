# Code snippets, check_localhost, and check_connectivity from Google Python for Automation course on Coursera

import ssl
import socket
import requests

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


# check network connectivity
def check_localhost():
    localhost = socket.gethostbyname('localhost')
    return localhost == '127.0.0.1'


# Check links on page connectivity
def check_connectivity(url):
    request = requests.get(url)
    return request.status_code == 200


# check for broken links, put messages in list
def link_status(url):
    try:
        page = requests.get(url, timeout=5)
        response_code = page.status_code
    except requests.exceptions.RequestException:
        return f"URL Connection UPDATE: <br> {url} <br> ❌ Error connecting. Check Link."

    if response_code == 200:
        return f"URL Connection UPDATE: <br> {url} <br> Status: 200 <br> Request Succeeded."
    else:
        return f"URL Connection UPDATE: <br> {url} <br> Status: {response_code} <br> Request Failed. Check Link."
