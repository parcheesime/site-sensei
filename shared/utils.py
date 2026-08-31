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
from http import HTTPStatus
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


def get_page_status(url):
    """Fetch a webpage once and return a structured, user-facing status."""
    try:
        response = requests.get(url, timeout=DEFAULT_REQUEST_TIMEOUT)
    except requests.exceptions.Timeout:
        return {
            'ok': False,
            'status_code': None,
            'reason': None,
            'label': 'Connection Error',
            'message': 'Site Sensei could not reach this webpage because the request timed out.',
            'content': None,
        }
    except requests.exceptions.ConnectionError:
        return {
            'ok': False,
            'status_code': None,
            'reason': None,
            'label': 'Connection Error',
            'message': 'Site Sensei could not reach this webpage.',
            'content': None,
        }
    except requests.exceptions.RequestException:
        return {
            'ok': False,
            'status_code': None,
            'reason': None,
            'label': 'Connection Error',
            'message': 'Site Sensei could not reach this webpage.',
            'content': None,
        }

    status_code = response.status_code
    reason = response.reason
    if not isinstance(reason, str) or not reason:
        try:
            reason = HTTPStatus(status_code).phrase
        except ValueError:
            reason = 'Unknown Status'

    label = f'HTTP Status: {status_code} {reason}'
    ok = 200 <= status_code < 300
    if ok:
        message = None
    elif status_code == 403:
        message = 'Site Sensei could not analyze this page because the server blocked the request.'
    elif status_code == 404:
        message = 'Site Sensei could not find this page.'
    else:
        message = 'Site Sensei could not analyze this page because the request was unsuccessful.'

    return {
        'ok': ok,
        'status_code': status_code,
        'reason': reason,
        'label': label,
        'message': message,
        'content': response.text,
    }


def clean_url(url):
    """
    Remove trailing /edit or /edit# from shared Code.org project links.
    """
    if not url:
        return ''
    return url.split('/edit')[0].strip()
