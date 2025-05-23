"""
linkchecks.py
--------------
Utility functions for checking network and URL connectivity
Used in the SiteSensei web page grading system.

These functions allow the grader to:
- Verify local networking is working (e.g., localhost)
- Check if a URL is reachable
- Report HTTP response status in formatted HTML

Originally adapted from the Google IT Automation with Python course.
"""

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


def clean_url(url):
    """
    Remove trailing /edit or /edit# from shared Code.org project links.
    """
    if not url:
        return ''
    return url.split('/edit')[0].strip()
