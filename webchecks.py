
# This code uses urllib to read the HTML from a URL,
# extract tags and frequency used, extract links and broken links

import re
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
        results[tag] = len(soup.find_all(tag))
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


def has_image_credit(url):
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        if 'credit' in p.get_text().lower() or 'image by' in p.get_text().lower():
            return True
    return False


def get_css_file_url(url):
    """Extracts the href for a linked CSS file from the HTML <link> tag."""
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')
    link_tag = soup.find('link', rel='stylesheet')
    if link_tag and link_tag.get('href'):
        href = link_tag['href']
        # Make absolute if it's relative
        if href.startswith('http'):
            return href
        else:
            base = url if url.endswith('/') else url.rsplit('/', 1)[0] + '/'
            return urllib.parse.urljoin(base, href)
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
    except Exception as e:
        return {
            'used': [],
            'missing': required_props,
            'message': f"❌ Error loading CSS file: {e}"
        }

    # Extract all property names from CSS using regex: matches "property-name:"
    all_props_used = set(re.findall(r'([a-zA-Z-]+)\s*:', css_text))
    found = [prop for prop in required_props if prop in all_props_used]
    missing = [prop for prop in required_props if prop not in all_props_used]

    message_lines = [
        f"✔️ CSS Property Summary:",
        f"- Total unique properties used: {len(all_props_used)}",
        f"- Properties used:\n" + ", ".join(sorted(all_props_used)),
        f"- Missing required properties:\n" + (", ".join(missing) if missing else "None 🎉"),
        f"- Found required properties: {found}"
    ]

    return {
        'used': sorted(all_props_used),
        'missing': missing,
        'message': "<br>".join(message_lines)
    }


# Create HTML page with message displayed
def html_output(feedback):
    with open('MST.html', 'w', encoding='utf-8') as html_pg:
        html_pg.write("<!DOCTYPE html><html>\n<head>\n<title> \n Teacher Feedback for Web Project \
           </title>\n</head> <body><h1>Your Results for the Web Page Project</h1>\
           \n<ul> {} </ul> \n</body></html>".format(feedback))
        return webbrowser.open('MST.html')
