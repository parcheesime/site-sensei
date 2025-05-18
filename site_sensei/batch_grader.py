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
from site_sensei.webpage_grader import generate_feedback_html, grade_student
from pathlib import Path
import html
import csv

# Define file paths
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

csv_file = DATA_DIR / "student_pages.csv"
output_file = DATA_DIR / "grades_output.csv"
html_file = DATA_DIR / "grades_feedback.html"


def grade_from_csv(csv_file, output_file, html_file):
    with open(csv_file, newline='', encoding='utf-8') as csv_in, \
         open(output_file, 'w', newline='', encoding='utf-8') as csv_out, \
         open(html_file, 'w', encoding='utf-8') as html_out:

        reader = csv.DictReader(csv_in)
        fieldnames = ['name', 'url', 'url_status', 'class_message', 'feedback']
        writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
        writer.writeheader()

        html_out.write("<html><head><title>Webpage Grading Feedback</title></head><body>\n")

        for row in reader:
            name = row.get('name', 'Unknown')
            url = row.get('url', '').strip()

            if not url:
                writer.writerow({
                    'name': name,
                    'url': '',
                    'url_status': '❌ No URL submitted',
                    'class_message': '',
                    'feedback': 'No webpage link found.'
                })
                html_out.write(f"<h3>{name}</h3><p>❌ No webpage submitted.</p><hr>\n")
                continue

            result = grade_student(url)
            writer.writerow({
                'name': name,
                'url': url,
                'url_status': result['url_status'],
                'class_message': result['class_message'],
                'feedback': result['feedback']
            })

            feedback_html = generate_feedback_html(url)
            html_out.write(f"<h2>{name}</h2>\n" + feedback_html)

        html_out.write(f"<h2>{html.escape(name)}</h2>\n" + feedback_html)
        print(f"✅ Grading complete! CSV saved to {output_file}, HTML saved to {html_file}")


if __name__ == "__main__":
    try:
        grade_from_csv(csv_file, output_file, html_file)
    except FileNotFoundError as e:
        print(f"❌ File not found: {e.filename}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
