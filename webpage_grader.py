from webchecks import get_links, get_class, get_tags, html_output
from webchecks import get_css_file_url, check_css_properties, has_image_credit
from linkchecks import link_status
import html
import requests
from bs4 import BeautifulSoup

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


def generate_smart_feedback(tag_counts):
    missing = [tag for tag in tags if tag_counts.get(tag, 0) == 0]
    if not missing:
        return "🎉 Great job! You included all required HTML tags."
    feedback = "<strong>Suggestions for Missing Tags:</strong><ul>"
    for tag in missing:
        suggestion = smart_explanations.get(tag, "Consider adding this tag to improve your page.")
        feedback += f"<li><code>&lt;{tag}&gt;</code>: {suggestion}</li>"
    feedback += "</ul>"
    return feedback


def generate_feedback_html(url):
    tag_counts = get_tags(url, list(smart_explanations.keys()))
    class_message = get_class(url)
    listof_links = get_links(url)
    page_links = [url + link for link in listof_links]
    page_links_status_messages = [link_status(link) for link in page_links if "html" in link]

    summary_items = []
    detail_items = []

    # Load page for title
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will throw if 404
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')
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
    summary_items.append(f"✔️ Paragraphs: {tag_counts.get('p', 0)}")
    summary_items.append(f"✔️ Lists: {tag_counts.get('li', 0)} items")
    summary_items.append(f"✔️ Images: {tag_counts.get('img', 0)}")

    # CSS analysis
    css_url = get_css_file_url(url)
    if css_url:
        css_check = check_css_properties(css_url)
        summary_items.append(f"✔️ CSS Selectors: {css_check['selector_count']}")
        summary_items.append(f"✔️ Unique CSS Properties: {len(css_check['used'])}")
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

    # Smart tag suggestions
    smart_feedback = generate_smart_feedback(tag_counts)

    # Format HTML output
    summary_html = ''.join(f"<li>{item}</li>\n" for item in summary_items)
    detail_html = ''.join(f"<li>{item}</li>\n" for item in detail_items)

    # Final render
    return f'''
    <h3><a href="{url}" target="_blank">{url}</a></h3>
    <ul>{summary_html}</ul>
    <ul>{detail_html}{smart_feedback}</ul>
    <hr>\n
    '''


def grade_student(url):
    tag_counts = get_tags(url, tags)
    class_message = get_class(url)
    url_status = link_status(url)
    listof_links = get_links(url)
    page_links = [url + link for link in listof_links if "html" in link]
    page_links_status_messages = [link_status(link) for link in page_links]

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
        "url_status": url_status,
        "class_message": class_message,
        "feedback": " | ".join(summary_items)
    }
