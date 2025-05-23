"""
script_grader.py
----------------
Batch grading script for JavaScript-based projects (e.g. Game Lab).

Reads a CSV file of student names and project URLs, analyzes the JS code,
and outputs:
1. A CSV summary of JS features used
2. An HTML file with detailed feedback per student

Usage:
    python script_grader.py data/student_pages.csv
"""

from js_grader.js_checks import grade_js_project
import csv
from pathlib import Path
from shared.utils import clean_url
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

# File setup
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
csv_file = DATA_DIR / "student_pages.csv"
output_file = DATA_DIR / "grades_output.csv"
html_file = DATA_DIR / "grades_feedback.html"

# Define JS-specific output fields
fieldnames = [
    'name', 'url', 'dominant_color', 'left_color', 'center_color', 'right_color', 'feedback_html'
]


def analyze_row(row):
    name = row.get('name', 'Unknown')
    url = clean_url(row.get('url', ''))
    result = grade_js_project(url)
    result['name'] = name
    result['url'] = url
    return result


def write_outputs(graded_rows, output_file, html_file):
    graded_rows.sort(key=lambda x: x['name'].lower())

    with open(output_file, 'w', newline='', encoding='utf-8') as csv_out:
        writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
        writer.writeheader()
        for row in graded_rows:
            row_data = {k: v for k, v in row.items() if k in fieldnames}
            writer.writerow(row_data)

    with open(html_file, 'w', encoding='utf-8') as html_out:
        html_out.write("<html><head><title>JS Project Feedback</title></head><body>\n")
        for row in graded_rows:
            html_out.write(f"<h2>{row['name']}</h2>\n")
            html_out.write(f"<p><strong>Project URL:</strong> <a href='{row['url']}' target='_blank'>{row['url']}</a></p>\n")
            html_out.write(f"<p><strong>Dominant Color:</strong> {row.get('dominant_color', 'N/A')}</p>\n")
            html_out.write(row.get('feedback_html', '') + "<hr>\n")
        html_out.write("</body></html>")


def grade_from_csv(csv_file, output_file, html_file):
    with open(csv_file, newline='', encoding='utf-8') as csv_in:
        reader = csv.DictReader(csv_in)
        graded_rows = [analyze_row(row) for row in reader]

    write_outputs(graded_rows, output_file, html_file)
    print(f"✅ JS CSV saved to: {output_file}")
    print(f"✅ JS HTML feedback saved to: {html_file}")


if __name__ == "__main__":
    grade_from_csv(csv_file, output_file, html_file)
