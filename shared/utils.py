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

DEFAULT_REQUEST_TIMEOUT = 10

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


# check network connectivity
def check_localhost():
    localhost = socket.gethostbyname('localhost')
    return localhost == '127.0.0.1'


def _url_status_message(url):
    try:
        page = requests.get(url, timeout=5)
        response_code = page.status_code
    except requests.exceptions.RequestException:
        return f"URL Connection UPDATE: <br> {url} <br> ❌ Error connecting. Check Link."

    if response_code == 200:
        return f"URL Connection UPDATE: <br> {url} <br> Status: 200 <br> Request Succeeded."
    else:
        return f"URL Connection UPDATE: <br> {url} <br> Status: {response_code} <br> Request Failed. Check Link."


def check_project_url(url):
    """Check the submitted project URL and return its user-facing status message."""
    return _url_status_message(url)


def check_page_link(url):
    """Check a link discovered in a project page and return its status message."""
    return _url_status_message(url)


def clean_url(url):
    """
    Remove trailing /edit or /edit# from shared Code.org project links.
    """
    if not url:
        return ''
    return url.split('/edit')[0].strip()
