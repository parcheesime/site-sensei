from webchecks import get_links, get_class, get_tags, html_output
from webchecks import get_css_file_url, check_css_properties, has_image_credit
from linkchecks import link_status

tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'img', 'li', 'br', 'a']


def generate_feedback_html(url):
    tag_counts = get_tags(url, tags)
    class_message = get_class(url)
    url_status_message = link_status(url)
    listof_links = get_links(url)
    page_links = [url + link for link in listof_links]
    page_links_status_messages = [link_status(link) for link in page_links if "html" in link]

    feedback_items = []

    # HTML Structure Checks
    feedback_items.append("✔️ Main Title Present" if tag_counts.get('h1', 0) >= 1 else "❌ Missing Main Title (<h1>)")
    
    subheadings_count = sum(tag_counts.get(tag, 0) for tag in ['h2', 'h3', 'h4', 'h5', 'h6'])
    feedback_items.append(f"✔️ Subheadings: {subheadings_count}" if subheadings_count >= 3 else f"❌ Only {subheadings_count} subheadings found (<h2>-<h6>)")
    
    feedback_items.append(f"✔️ Paragraphs: {tag_counts.get('p', 0)}" if tag_counts.get('p', 0) >= 3 else f"❌ Only {tag_counts.get('p', 0)} paragraph(s)")
    
    feedback_items.append(f"✔️ Lists: {tag_counts.get('li', 0)} items" if tag_counts.get('li', 0) >= 3 else f"❌ Only {tag_counts.get('li', 0)} list items")
    
    feedback_items.append(f"✔️ Images: {tag_counts.get('img', 0)}" if tag_counts.get('img', 0) >= 3 else f"❌ Only {tag_counts.get('img', 0)} image(s)")

    # CSS Checks
    feedback_items.append(class_message)
    css_url = get_css_file_url(url)
    if css_url:
        css_check = check_css_properties(css_url)
        feedback_items.append(css_check['message'])
    else:
        feedback_items.append("❌ No external CSS file found.")

    # # Link checks
    # if not page_links_status_messages:
    #     feedback_items.append("❌ Missing or invalid link to another HTML page.")
    # else:
    #     feedback_items.extend([f"✔️ {msg}" for msg in page_links_status_messages])
     
    # Image credit check
    if has_image_credit(url):
        feedback_items.append("✔️ Image credit found in paragraph.")
    else:
        feedback_items.append("❌ Missing image credit in paragraph.")

    # Format as HTML
    html_items = ''.join(f"<li>{item}</li>\n" for item in feedback_items)
    return f'<h3><a href="{url}" target="_blank">{url}</a></h3><ul>{html_items}</ul><hr>\n'


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
