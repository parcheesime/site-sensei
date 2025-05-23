"""
batch_grader.py
---------------
Batch grading script for SiteSensei.

This script reads a CSV file containing student names and project URLs,
grades each student's webpage using the `grade_student` function, and
generates two output files:
1. A CSV summary of grading results
2. An HTML file with detailed feedback for each student

Inputs and outputs are managed in the `data/` directory.

How to use:
-----------
Run from the command line:
    python batch_grader.py data/student_pages.csv

Dependencies:
-------------
- Python 3.x
- webpage_grader.py (contains grading logic)
- data/student_pages.csv (input list of student URLs)

Author: Sensei Trepte
"""

# Imports
from shared.webchecks import (
    count_broken_tags, count_comments, get_tags,
    get_css_file_url, check_css_properties
)
import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
from student_mode.webpage_grader import generate_feedback_html


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
csv_file = DATA_DIR / "student_pages.csv"
output_file = DATA_DIR / "grades_output.csv"
html_file = DATA_DIR / "grades_feedback.html"

smart_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'img']

fieldnames = [
    'name', 'url', 'title', 'subheading_total', 'paragraph_count',
    'list_count', 'image_count', 'css_selectors', 'css_properties',
    'tag_mismatches', 'html_comments'
]


def analyze_student_row(row):
    name = row.get('name', 'Unknown')
    url = row.get('url', '').strip()

    if not url:
        return {
            'name': name, 'url': '', 'title': 'Missing',
            'subheading_total': 'N/A', 'paragraph_count': 'N/A',
            'list_count': 'N/A', 'image_count': 'N/A',
            'css_selectors': 'N/A', 'css_properties': 'N/A',
            'tag_mismatches': 'N/A', 'html_comments': 'N/A',
            'feedback_html': f"<h2>{name}</h2><p>❌ No webpage submitted.</p><hr>\n"
        }

    try:
        tag_counts = get_tags(url, smart_tags)
    except Exception:
        tag_counts = {}

    try:
        h1_text = BeautifulSoup(requests.get(url).text, 'html.parser')\
                    .find('h1').get_text(strip=True)
    except Exception:
        h1_text = "Missing"

    subheading_total = sum(tag_counts.get(tag, 0) for tag in ['h2', 'h3', 'h4', 'h5', 'h6'])

    try:
        css_url = get_css_file_url(url)
        if css_url:
            css_result = check_css_properties(css_url)
            css_selectors = css_result['selector_count']
            css_properties = len(css_result['used'])
        else:
            css_selectors = css_properties = "N/A"
    except Exception:
        css_selectors = css_properties = "Error"

    try:
        tag_mismatches = count_broken_tags(url)
        mismatch_count = len(tag_mismatches) if isinstance(tag_mismatches, dict) else "Error"
    except Exception:
        mismatch_count = "Error"

    try:
        html_comments = count_comments(url)
    except Exception:
        html_comments = "Error"

    try:
        feedback_html = generate_feedback_html(url)
    except Exception:
        feedback_html = "<p>❌ Could not generate detailed feedback.</p>"

    return {
        'name': name,
        'url': url,
        'title': h1_text,
        'subheading_total': subheading_total,
        'paragraph_count': tag_counts.get('p', 0),
        'list_count': tag_counts.get('li', 0),
        'image_count': tag_counts.get('img', 0),
        'css_selectors': css_selectors,
        'css_properties': css_properties,
        'tag_mismatches': mismatch_count,
        'html_comments': html_comments,
        'feedback_html': f"<h2>{name} – {h1_text}</h2>\n" + feedback_html
    }


def write_outputs(graded_rows, output_file, html_file):
    graded_rows.sort(key=lambda x: x['name'].lower())

    with open(output_file, 'w', newline='', encoding='utf-8') as csv_out:
        writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
        writer.writeheader()
        for row in graded_rows:
            row_data = {k: v for k, v in row.items() if k in fieldnames}
            writer.writerow(row_data)

    with open(html_file, 'w', encoding='utf-8') as html_out:
        html_out.write("<html><head><title>Webpage Grading Feedback</title></head><body>\n")
        for row in graded_rows:
            html_out.write(row['feedback_html'])
        html_out.write("</body></html>")


def grade_from_csv(csv_file, output_file, html_file):
    with open(csv_file, newline='', encoding='utf-8') as csv_in:
        reader = csv.DictReader(csv_in)
        graded_rows = [analyze_student_row(row) for row in reader]

    write_outputs(graded_rows, output_file, html_file)
    print(f"✅ Summary CSV saved to: {output_file}")
    print(f"✅ HTML feedback saved to: {html_file}")


if __name__ == "__main__":
    try:
        grade_from_csv(csv_file, output_file, html_file)
    except FileNotFoundError as e:
        print(f"❌ File not found: {e.filename}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
