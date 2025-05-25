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
```
SITE-SENSEI/
├── pycache/
├── .github/
├── data/
├── js_grader/
├── myenv/
├── shared/
├── static/
├── student_mode/
├── teacher_mode/
├── templates/
├── tests/
├── .gitignore
├── app.py
├── LICENSE
├── README.md
└── requirements.txt
```

1. Run batch grader

python teacher_mode/batch_grader.py data/student_pages.csv

2. Start the web app

python app.py

Then open your browser to http://127.0.0.1:5000

---

## 📥 CSV Format Example

name,url

Alice,https://example.com/page1

Bob,https://example.com/page2

---

## 🔐 Licensing & Use

Site Sensei is released under the MIT License.

This tool is developed for educational use.