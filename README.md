# Site Sensei

## 🎯 Purpose
Site Sensei is meant to be a web page grader that helps middle school students and teachers evaluate HTML and CSS projects quickly and consistently. Students receive immediate feedback on the structure and quality of their web pages, while teachers can speed grade entire classes with a single script. This is a WIP.

## 💡 Key Features

### For Teachers
- Grade an entire class by importing a CSV with student names and project URLs
- Output:
  - A structured CSV file with summary feedback
  - An HTML file (`grades_feedback.html`) with detailed, clickable feedback per student

🚧 Coming Soon
### For Students
- Self-check by entering a project URL
- Instant feedback on:
  - Required HTML tags (headings, paragraphs, images, lists, etc.)
  - Use of the `class` attribute and external CSS
  - Working links to additional HTML pages
  - Presence of image credits

## ⚙️ How It Works

### Individual Use
1. Call `generate_feedback_html(url)` with a student's project URL.
2. An HTML report is returned with detailed feedback.

### Batch Grading
1. Prepare a CSV file like this:

   ```csv
   name,url
   Alice,https://codeprojects.org/your-page
   Bob,https://codeprojects.org/another-page

Run the batch grader:

bash
Copy
Edit
python batch_grader.py student_pages.csv
You’ll get:

grades_output.csv — summary feedback for each student

grades_feedback.html — full clickable report for all students

🧪 Technologies Used
Python 3

Beautiful Soup (HTML parsing)

Requests (link and CSS validation)

📁 Folder Structure
Copy
Edit
web-page-grader/
├── batch_grader.py
├── webpage_grader.py
├── webchecks.py
├── linkchecks.py
├── student_pages.csv
├── grades_output.csv
└── grades_feedback.html
🚧 Coming Soon
Support for JavaScript-based Game Lab projects

Scoring rubric integration

Option for generating individual HTML reports per student

Student-facing web form version (for Chromebook-friendly self-check)

👩‍🏫 Ideal For
Computer Science teachers using Google Classroom

Students working on Code.org, CodeProjects, or other beginner-friendly web editors

📝 License
MIT License