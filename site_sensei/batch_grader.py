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
from site_sensei.webchecks import (
    count_broken_tags, count_comments, get_tags,
    get_css_file_url, check_css_properties
)
import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
csv_file = DATA_DIR / "student_pages.csv"
output_file = DATA_DIR / "grades_output.csv"
html_file = DATA_DIR / "grades_feedback.html"

smart_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'img']


def grade_from_csv(csv_file, output_file, html_file):
    with open(csv_file, newline='', encoding='utf-8') as csv_in, \
         open(output_file, 'w', newline='', encoding='utf-8') as csv_out, \
         open(html_file, 'w', encoding='utf-8') as html_out:

        reader = csv.DictReader(csv_in)
        fieldnames = [
            'url', 'title', 'subheading_total', 'paragraph_count',
            'list_count', 'image_count', 'css_selectors', 'css_properties',
            'tag_mismatches', 'html_comments'
        ]
        writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
        writer.writeheader()

        html_out.write("<html><head><title>Webpage Grading Feedback</title></head><body>\n")

        for row in reader:
            url = row.get('url', '').strip()

            if not url:
                writer.writerow({key: 'N/A' for key in fieldnames})
                html_out.write(f"<h3>❌ No webpage submitted.</h3><hr>\n")
                continue

            # Get HTML
            try:
                html_text = requests.get(url).text
                soup = BeautifulSoup(html_text, 'html.parser')
            except Exception:
                writer.writerow({key: 'Error' for key in fieldnames})
                html_out.write(f"<h3>{url}</h3><p>❌ Could not load page.</p><hr>\n")
                continue

            # Title from H1
            h1_elements = soup.find_all('h1')
            title = h1_elements[0].get_text(strip=True) if h1_elements else "Missing"

            # Tag counts
            tag_counts = get_tags(url, smart_tags)
            subheading_total = sum(tag_counts.get(tag, 0) for tag in ['h2', 'h3', 'h4', 'h5', 'h6'])

            # CSS
            css_url = get_css_file_url(url)
            if css_url:
                css_result = check_css_properties(css_url)
                css_selectors = css_result['selector_count']
                css_properties = len(css_result['used'])
            else:
                css_selectors = css_properties = "N/A"

            # Other metrics
            tag_mismatches = count_broken_tags(url)
            mismatch_count = len(tag_mismatches) if isinstance(tag_mismatches, dict) else "Error"
            html_comments = count_comments(url)

            writer.writerow({
                'url': url,
                'title': title,
                'subheading_total': subheading_total,
                'paragraph_count': tag_counts.get('p', 0),
                'list_count': tag_counts.get('li', 0),
                'image_count': tag_counts.get('img', 0),
                'css_selectors': css_selectors,
                'css_properties': css_properties,
                'tag_mismatches': mismatch_count,
                'html_comments': html_comments
            })

            # HTML feedback output (unchanged)
            from site_sensei.webpage_grader import generate_feedback_html
            feedback_html = generate_feedback_html(url)
            html_out.write(f"<h2>{title}</h2>\n" + feedback_html)

        html_out.write("</body></html>")
        print(f"✅ Summary CSV saved to: {output_file}")
        print(f"✅ HTML feedback saved to: {html_file}")


if __name__ == "__main__":
    try:
        grade_from_csv(csv_file, output_file, html_file)
    except FileNotFoundError as e:
        print(f"❌ File not found: {e.filename}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
