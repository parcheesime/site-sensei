# 🧠 Site Sensei

**Site Sensei** is a grading tool that helps students and teachers evaluate web development projects. It currently supports HTML and CSS analysis and is built for **educational purposes**.

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
- Upload a CSV with student URLs and view or download:
  - `grades_output.csv` (summary)
  - `grades_feedback.html` (detailed clickable feedback)

### 🔁 Command-Line Batch Grading

- Grades the projects listed in `data/student_pages.csv`
- Writes `data/grades_output.csv` and `data/grades_feedback.html`

---

## 🚀 Quick Start

Site Sensei currently runs on WSL/Linux with Python 3.12. From a WSL/Linux shell:

```bash
git clone https://github.com/parcheesime/site-sensei.git
cd site-sensei
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The local `.venv/` directory is ignored by Git.

## ▶️ Running Site Sensei

Run commands from the repository root with the virtual environment activated.

### Flask Web App

```bash
python app.py
```

Then open <http://127.0.0.1:5000> in your browser. The teacher interface accepts a CSV upload or a Google Sheet link and writes grading results under `data/`.

### Teacher Batch Grader

Place the input CSV at `data/student_pages.csv`, then run:

```bash
python -m teacher_mode.batch_grader
```

The batch grader creates:

- `data/grades_output.csv` — grading summary
- `data/grades_feedback.html` — detailed HTML feedback

The CSV must contain a header row with `name` and `url` columns:

```csv
name,url
Alice,https://example.com/page1
Bob,https://example.com/page2
```

Each subsequent row represents one student. A missing `url` is reported as a missing submission.

### Test Suite

```bash
python -m pytest
```

The test suite covers shared URL checks, HTML checks, grader integration, and container configuration without requiring Docker or a browser.

### Optional Experimental Visual Check

Selenium/Game Lab support is experimental and is not part of the normal pytest run. The manual visual snapshot script requires a compatible browser and browser driver and may download a driver through `webdriver-manager`:

```bash
python scripts/visual_snapshot_check.py
```

The script captures a browser-rendered screenshot under `data/screenshots/` and updates `data/test_feedback.html`. It is a browser-dependent experiment, not complete JavaScript or Game Lab grading.

## 🐳 Docker Compose

Docker provides a local app container and an internal Selenium Chrome service. Docker Desktop with WSL integration (or Docker Engine with the Compose plugin) is required; this is a development foundation, not a finished one-click teacher installer.

Start both services from the repository root:

```bash
docker compose up --build
```

Open <http://localhost:5000> to use the Flask interface. The Selenium server is available to the app at `http://selenium:4444` on the internal Compose network and is not published to the host.

The host's `data/` directory is mounted at `/app/data`. Place or upload the teacher CSV as `data/student_pages.csv`. Generated files remain on the teacher's computer at:

- `data/grades_output.csv`
- `data/grades_feedback.html`
- `data/screenshots/` and `data/test_feedback.html` when the optional visual utility runs

Run the teacher batch grader inside the app container with:

```bash
docker compose exec app python teacher_mode/batch_grader.py data/student_pages.csv
```

Selenium is optional for normal HTML/CSS grading. If an experimental browser check reports that Selenium is unavailable, inspect service health and logs:

```bash
docker compose ps
docker compose logs selenium
```

Chrome images require substantial memory and shared memory. Wait for the Selenium service to become healthy before retrying a visual check. No Selenium debugging port is exposed by default.

Stop and remove the containers without deleting host reports:

```bash
docker compose down
```

The WSL/Python Quick Start above remains available for development without Docker.

---

## 🧪 Technologies Used

| Tool | Purpose |
|------|---------|
| Python 3.12 | Core scripting language |
| Flask | Web app interface |
| Beautiful Soup | HTML parsing and tag checking |
| Requests | Link and CSS validation |
| Selenium | Experimental browser-rendered checks |
| Pillow | Screenshot and image processing |
| pytest | Automated test suite |
| CSV / pathlib | File and grading-output management |

---

## 🗂️ Folder Structure

```text
site-sensei/
├── .github/            # GitHub configuration
├── .dockerignore       # Docker build-context exclusions
├── data/               # CSV inputs, reports, and visual-check output
├── js_grader/          # Experimental browser-based grading code
├── scripts/            # Manual utilities and Selenium experiments
├── shared/             # Shared networking and HTML helpers
├── static/             # CSS and image assets
├── student_mode/       # Individual webpage grading logic
├── teacher_mode/       # Batch grading logic
├── templates/          # Flask HTML templates
├── tests/              # pytest test suite
├── compose.yaml        # App and Selenium services
├── Dockerfile          # Python application image
├── app.py              # Flask application entry point
├── LICENSE
├── README.md
└── requirements.txt
```

---

## 🚧 Roadmap (Coming Soon)

- [ ] Game Lab project analysis (JavaScript/sprite logic detection)
- [ ] Rubric scoring system with customizable criteria
- [ ] Option to generate individual student reports
- [ ] Chromebook-friendly self-check form for students
- [ ] Teacher dashboard with class overview

---

## 🔐 Licensing & Use

### Notice

SiteSensei is visible for portfolio, demonstration, planning, and discussion purposes only.

No license is granted to reuse the code, documentation, database schema, architecture, prompts, workflows, or educational knowledge model.

Contact the copyright holder for licensing inquiries.
