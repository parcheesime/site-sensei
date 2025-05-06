from webpage_grader import generate_feedback_html, grade_student
import csv


def grade_from_csv(csv_file, output_file="grades_output.csv", html_file="grades_feedback.html"):
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

        html_out.write("</body></html>")
        print(f"✅ Grading complete! CSV saved to {output_file}, HTML saved to {html_file}")

   
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("❌ Please provide a CSV file to grade.\nUsage: python batch_grader.py student_pages.csv")
    else:
        csv_input = sys.argv[1]
        grade_from_csv(csv_input)