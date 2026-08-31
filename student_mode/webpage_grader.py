"""
webpage_grader.py
-----------------
Main grading and feedback logic for the SiteSensei project.

This script evaluates individual student web pages by checking for:
- Required HTML tags and structure
- CSS usage and external stylesheet presence
- Image credit in content
- Class attribute usage
- Working links to additional HTML pages

Functions:
----------
- grade_student(url): Returns a quick grading summary used in CSV output
- generate_feedback_html(url): Builds detailed feedback in formatted HTML

Dependencies:
-------------
- webchecks.py for tag analysis, class detection, CSS file extraction
- linkchecks.py for validating URL connectivity
- BeautifulSoup and requests for page parsing and HTML evaluation
"""

import html
import urllib.parse
from bs4 import BeautifulSoup
from shared.webchecks import (
    get_links, get_class, get_tags, get_css_file_url,
    check_css_properties, has_image_credit,
    count_broken_tags, count_comments
)
from shared.utils import check_page_link, get_page_status


# Smart tag explanations
smart_explanations = {
    'h1': "Use a main heading to introduce your webpage clearly.",
    'h2': "Subheadings help organize sections and make your content easier to follow.",
    'p': "Paragraph tags help break up your writing into readable chunks.",
    'img': "Images enhance your page and can visually explain your content.",
    'li': "List items are useful for organizing related information.",
    'a': "Anchor tags link to other pages or resources — an important navigation tool.",
    'br': "Line breaks help with spacing and layout without starting a new paragraph.",
    'h3': "Tertiary headings can be used to organize subsections under subheadings.",
    'h4': "Use this heading level for fine-tuned structure in detailed pages.",
    'h5': "Helps with nested content or accessibility structure.",
    'h6': "Rarely used but useful for deeply nested information structure."
}


tags = list(smart_explanations.keys())
HTML_TAG_TYPE_TARGET = 8
CSS_PROPERTY_TARGET = 8


def get_html_page_links(base_url, links):
    """Return valid, absolute links whose URL path targets an HTML page."""
    page_links = []
    for link in links:
        if not isinstance(link, str) or not link.strip():
            continue

        absolute_url = urllib.parse.urljoin(base_url, link)
        path = urllib.parse.urlparse(absolute_url).path.lower()
        if path.endswith(('.html', '.htm')):
            page_links.append(absolute_url)

    return page_links


def render_page_status(url, page_status):
    """Render the submitted URL and its retrieval status for either grading mode."""
    escaped_url = html.escape(url, quote=True)
    escaped_label = html.escape(page_status['label'])
    status_html = (
        f'<h3><a href="{escaped_url}" target="_blank" rel="noopener noreferrer">'
        f'{escaped_url}</a></h3>\n'
        f'<p><strong>{escaped_label}</strong></p>\n'
    )
    if page_status['message']:
        status_html += f"<p>{html.escape(page_status['message'])}</p>\n"
    return status_html


def generate_smart_feedback(tag_counts):
    missing = [tag for tag in tags if tag_counts.get(tag, 0) == 0]
    if not missing:
        return "🎉 Great job! You included every HTML tag type checked by Site Sensei."
    feedback = "<strong>Suggestions for Missing Tags:</strong><ul>"
    for tag in missing:
        suggestion = smart_explanations.get(tag, "Consider adding this tag to improve your page.")
        feedback += f"<li><code>&lt;{tag}&gt;</code>: {suggestion}</li>"
    feedback += "</ul>"
    return feedback


def generate_feedback_html(url, page_status=None):
    if page_status is None:
        page_status = get_page_status(url)

    status_html = render_page_status(url, page_status)
    if not page_status['ok']:
        return f'{status_html}<hr>\n'

    tag_counts = get_tags(url, list(smart_explanations.keys()))
    class_message = get_class(url)
    listof_links = get_links(url)
    page_links = get_html_page_links(url, listof_links)
    page_links_status_messages = [check_page_link(link) for link in page_links]

    summary_items = []
    detail_items = []

    # The successful status request also supplies the page used for title parsing.
    try:
        soup = BeautifulSoup(page_status['content'], 'html.parser')
        h1_elements = soup.find_all('h1')
        if h1_elements:
            title_text = h1_elements[0].get_text(strip=True)
            summary_items.append(f'✔️ Main Title: "{html.escape(title_text)}"')
        else:
            summary_items.append(f"❌ Missing Main Title ({html.escape('<h1>')})")
    except Exception:
        summary_items.append(f"❌ Error loading page to check {html.escape('<h1>')} tag.")

    # Subheadings
    subheading_tags = ['h2', 'h3', 'h4', 'h5', 'h6']
    subheading_count = sum(tag_counts.get(tag, 0) for tag in subheading_tags)
    subheading_breakdown = [f"{tag.upper()}: {tag_counts.get(tag, 0)}" for tag in subheading_tags if tag_counts.get(tag, 0) > 0]
    summary_items.append(
        f"✔️ Subheadings: {subheading_count} ({', '.join(subheading_breakdown)})" if subheading_count > 0 
        else "❌ No subheadings (&lt;h2&gt;-&lt;h6&gt;)"
    )

    # Tag tallies
    html_tag_type_count = sum(1 for tag in tags if tag_counts.get(tag, 0) > 0)
    tag_target_icon = "✔️" if html_tag_type_count >= HTML_TAG_TYPE_TARGET else "❌"
    summary_items.append(
        f"{tag_target_icon} HTML tag types: {html_tag_type_count} "
        f"(target: {HTML_TAG_TYPE_TARGET}+)"
    )
    summary_items.append(f"✔️ Paragraphs: {tag_counts.get('p', 0)}")
    summary_items.append(f"✔️ Lists: {tag_counts.get('li', 0)} items")
    summary_items.append(f"✔️ Images: {tag_counts.get('img', 0)}")

    # CSS analysis
    css_url = get_css_file_url(url)
    if css_url:
        css_check = check_css_properties(css_url)
        css_property_count = len(css_check['used'])
        css_target_icon = "✔️" if css_property_count >= CSS_PROPERTY_TARGET else "❌"
        summary_items.append(f"✔️ CSS Selectors: {css_check['selector_count']}")
        summary_items.append(
            f"{css_target_icon} CSS properties: {css_property_count} "
            f"(target: {CSS_PROPERTY_TARGET}+)"
        )
        detail_items.append(css_check['message'])
    else:
        summary_items.append("❌ No external CSS file found.")
        detail_items.append("❌ CSS file could not be loaded.")

    # Class usage
    detail_items.append(class_message)

    # Link check
    if not page_links_status_messages:
        detail_items.append("❌ Missing or invalid link to another HTML page.")
    else:
        detail_items.extend([f"✔️ {msg}" for msg in page_links_status_messages])

    # Image credit
    detail_items.append("✔️ Image credit found in paragraph." if has_image_credit(url) else "❌ Missing image credit in paragraph.")

    # Broken tag check (moved up to summary, no breakdown)
    tag_mismatches = count_broken_tags(url)
    clean_mismatches = {tag: diff for tag, diff in tag_mismatches.items() if tag.strip()}

    if clean_mismatches:
        summary_items.append(f"❌ {len(clean_mismatches)} Tag Mismatches Found:")
    else:
        summary_items.append("✔️ No broken tags detected.")

    # Comment count (also moved to summary)
    num_comments = count_comments(url)
    summary_items.append(f"✔️ HTML Comments Found: {num_comments}")

    # Smart tag suggestions
    smart_feedback = generate_smart_feedback(tag_counts)

    # Format HTML output
    summary_html = ''.join(f"<li>{item}</li>\n" for item in summary_items)
    detail_html = ''.join(f"<li>{item}</li>\n" for item in detail_items)

    # Final render
    return f'''
    {status_html}
    <ul>{summary_html}</ul>
    <ul>{detail_html}{smart_feedback}</ul>
    <hr>\n
    '''


def grade_student(url, page_status=None):
    if page_status is None:
        page_status = get_page_status(url)
    if not page_status['ok']:
        return {
            'url_status': page_status['label'],
            'class_message': page_status['message'],
            'feedback': '❌ Page not analyzed',
        }

    tag_counts = get_tags(url, tags)
    class_message = get_class(url)
    listof_links = get_links(url)
    page_links = get_html_page_links(url, listof_links)
    page_links_status_messages = [check_page_link(link) for link in page_links]

    summary_items = []

    if tag_counts.get('h1', 0) >= 1:
        summary_items.append("✔️ H1")
    else:
        summary_items.append("❌ No H1")

    if tag_counts.get('p', 0) >= 3:
        summary_items.append("✔️ Paragraphs")
    else:
        summary_items.append("❌ Few Paragraphs")

    if tag_counts.get('img', 0) >= 3:
        summary_items.append("✔️ Images")
    else:
        summary_items.append("❌ Few Images")

    if class_message and "✔️" in class_message:
        summary_items.append("✔️ Class")
    else:
        summary_items.append("❌ Class Missing")

    if page_links_status_messages:
        summary_items.append("✔️ Link")
    else:
        summary_items.append("❌ No HTML Link")

    return {
        "url_status": page_status['label'],
        "class_message": class_message,
        "feedback": " | ".join(summary_items)
    }
