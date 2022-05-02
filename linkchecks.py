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
    page = requests.get(url)
    response_code = str(page.status_code)
    if response_code == "200":
        status = "URL Connection UPDATE: <br> {} <br> Status: {} <br> Request Succeeded.".format(url, response_code)
    else:
        status = "URL Connection UPDATE: <br> {} <br> Status: {} <br> Request Failed. Check Link.".format(url, response_code)
    return status
