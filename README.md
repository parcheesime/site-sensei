# 🧠 Site Sensei

**Site Sensei** is a free and open-source grading tool that helps students and teachers evaluate web development projects. It currently supports HTML and CSS analysis and is built for **educational purposes**.

---

## 🎯 Purpose

Site Sensei provides structured, automated feedback on student web pages. It was created to help:
- **Teachers** batch-grade student websites more efficiently
- **Students** get immediate feedback and improve independently

---

## 💡 Key Features

### ✅ HTML/CSS Grading (Core)
- Detects and evaluates:
  - HTML structure: `head`, `body`, `h1`, `p`, `img`, `ul`, `a`, etc.
  - Use of `class` attributes and external CSS
  - Presence of image credits
  - Working links to other pages

### 🌐 Web App Interface
- Teacher-facing web interface built with Flask
- Upload a CSV with student URLs and instantly view/download:
  - `grades_output.csv` (summary)
  - `grades_feedback.html` (detailed clickable feedback)

### 🔁 Command Line Batch Grading
- Run `python batch_grader.py data/student_pages.csv`
- Automatically grades each project and exports:
  - CSV summary with grades
  - HTML report with inline comments and structure flags

---

## 🚧 Roadmap (Coming Soon)

- [ ] Game Lab project analysis (JavaScript/sprite logic detection)
- [ ] Rubric scoring system with customizable criteria
- [ ] Option to generate individual student reports
- [ ] Chromebook-friendly self-check form for students
- [ ] Teacher dashboard with class overview

---

## 🧪 Technologies Used

| Tool            | Purpose                          |
|-----------------|----------------------------------|
| Python 3        | Core scripting language          |
| Flask           | Web app interface                |
| BeautifulSoup   | HTML parsing and tag checking    |
| Requests        | Link and CSS validation          |
| CSV / pathlib   | File management                  |

---

## 🗂️ Folder Structure

site-sensei/
├── app.py # Flask entry point
├── templates/ # HTML templates for web app
│ └── index.html, results.html, etc.
├── static/ # Optional styles/scripts
├── data/ # CSV input/output files
│ ├── student_pages.csv
│ ├── grades_output.csv
│ └── grades_feedback.html
├── teacher_mode/
│ └── batch_grader.py # CSV-based grading script
├── student_mode/
│ └── webpage_grader.py # Per-student grading logic
├── shared/
│ ├── webchecks.py # HTML checks and tag validation
│ ├── linkchecks.py # Broken link and CSS checkers
│ └── utils.py # CSV reading, formatting helpers
└── README.md

2. Run batch grader

python teacher_mode/batch_grader.py data/student_pages.csv

3. Start the web app

python app.py

Then open your browser to http://127.0.0.1:5000

## 📥 CSV Format Example

name,url

Alice,https://codeprojects.org/your-page

Bob,https://codeprojects.org/another-page

## 🔐 Licensing & Use

Site Sensei is released under the MIT License.

This tool is developed for educational use.