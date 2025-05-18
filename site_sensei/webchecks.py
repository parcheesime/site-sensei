
"""
webchecks.py
------------
Functions to analyze student web pages for:
- HTML tag usage
- Presence of class attributes
- Linked page URLs
- Image credits
- External CSS file structure

These tools are part of the SiteSensei web grading system and are used to generate structured feedback for student submissions.
"""

import re
import ssl
import urllib.parse
import urllib.request
from pathlib import Path
import webbrowser
import requests
from bs4 import BeautifulSoup
from collections import Counter

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


# Retrieve tags frequency dictionary, according to list of tags
def get_tags(url, tag_list):
    try:
        html = urllib.request.urlopen(url, context=ctx).read()
    except Exception:
        return {tag: 0 for tag in tag_list}

    soup = BeautifulSoup(html, 'html.parser')
    return {tag: len(soup.find_all(tag)) for tag in tag_list}


def count_broken_tags(url):
    """
    Estimate broken/missing HTML tags on the page.

    Args:
        url (str): The URL of the student's page.

    Returns:
        dict: Tag mismatch counts (tag -> difference in open/close).
    """
    try:
        html = urllib.request.urlopen(url, context=ctx).read().decode('utf-8')
        open_tags = re.findall(r'<([a-zA-Z0-9]+)(\s|>)', html)
        close_tags = re.findall(r'</([a-zA-Z0-9]+)>', html)

        open_counter = Counter(tag for tag, _ in open_tags)
        close_counter = Counter(close_tags)

        mismatches = {}
        for tag in set(open_counter.keys()).union(close_counter.keys()):
            diff = open_counter[tag] - close_counter[tag]
            if diff != 0:
                mismatches[tag] = diff

        return mismatches
    except Exception as e:
        return {"error": str(e)}


# Check for CSS clss selectors, using requests.get
def get_class(url):
    try:
        page = requests.get(url)
    except Exception:
        return Exception
    data = page.text
    data = data.split()
    count_class = [ele for ele in data if 'class' in ele]
    return "CSS UPDATE: <br> Class attribute is used {} time(s).".format(len(count_class))


# Get list of URL on webpage
def get_links(url):
    try:
        html = urllib.request.urlopen(url, context=ctx).read()
    except Exception:
        return Exception
    soup = BeautifulSoup(html, 'html.parser')
    # Retrieve anchor tags, make a list of urls
    tags = soup('a')
    urllist = [tag.get('href', None) for tag in tags]
    return urllist


def has_image_credit(url):
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        if 'credit' in p.get_text().lower() or 'image by' in p.get_text().lower():
            return True
    return False


def count_comments(url):
    """
    Count the number of HTML comments on the page.

    Args:
        url (str): The URL of the student's page.

    Returns:
        int: Number of HTML comments.
    """
    try:
        html = urllib.request.urlopen(url, context=ctx).read()
        soup = BeautifulSoup(html, 'html.parser')
        comments = soup.find_all(string=lambda text: isinstance(text, type(soup.comment)))
        return len(comments)
    except Exception:
        return 0


def get_css_file_url(url):
    try:
        # Load HTML
        html_bytes = urllib.request.urlopen(url, context=ctx).read()
        html_string = html_bytes.decode("utf-8")

        # Match student-linked style.css (case-insensitive)
        match = re.search(r'<link[^>]+href=["\'](style\.css)["\']', html_string, re.IGNORECASE)
        if match:
            # Ensure project URL ends in the project ID folder
            match_base = re.match(r'(https://codeprojects\.org/projects/weblab/[^/]+)', url)
            if match_base:
                base_url = match_base.group(1) + '/'
                full_url = urllib.parse.urljoin(base_url, "style.css")
                print(f"[DEBUG ✅] Found student style.css: {full_url}")
                return full_url
            else:
                print(f"[ERROR] Could not extract project base from {url}")
                return None

        print(f"[WARN] No student style.css found in HTML for {url}")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to resolve CSS for {url}: {e}")
        return None


def check_css_properties(css_url, required_props=None):
    if required_props is None:
        required_props = [
            'font-family', 'margin', 'float',
            'color', 'background-color',
            'border', 'border-radius', 'font-size'
        ]

    try:
        css_text = requests.get(css_url).text
        selector_count = css_text.count('{')
    except Exception as e:
        return {
            'used': [],
            'missing': required_props,
            'selector_count': 0,
            'message': f"❌ Error loading CSS file: {e}"
        }

    # Extract property names from CSS (e.g., font-size:)
    all_props_used = set(re.findall(r'([a-zA-Z-]+)\s*:', css_text))
    found = [prop for prop in required_props if prop in all_props_used]
    missing = [prop for prop in required_props if prop not in all_props_used]

    message_lines = [
        "✔️ CSS Property Summary:",
        f"- Total unique properties used: {len(all_props_used)}",
        f"- Properties used: {', '.join(sorted(all_props_used))}",
        f"- Missing required properties: {', '.join(missing) if missing else 'None 🎉'}",
        f"- Found required properties: {found}",
        f"- Total unique CSS selectors: {selector_count}"
    ]

    return {
        'used': sorted(all_props_used),
        'missing': missing,
        'selector_count': selector_count,
        'message': "<br>".join(message_lines)
    }


# Create HTML page with message displayed
def html_output(feedback):
    STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
    MST_FILE = STATIC_DIR / "MST.html"

    with open(MST_FILE, 'w', encoding='utf-8') as html_pg:
        html_pg.write(
            "<!DOCTYPE html><html>\n<head>\n<title>Teacher Feedback for Web Project</title>\n"
            "</head><body><h1>Your Results for the Web Page Project</h1>\n<ul>{}</ul>\n"
            "</body></html>".format(feedback)
        )

    return webbrowser.open(MST_FILE.as_uri())
