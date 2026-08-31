from flask import (
    Flask, flash, redirect, render_template, request, send_file,
    send_from_directory, url_for,
)
from teacher_mode.batch_grader import grade_from_csv
from student_mode.webpage_grader import generate_feedback_html
from shared.utils import DEFAULT_REQUEST_TIMEOUT
import requests
import os

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    if not app.debug:
        raise RuntimeError(
            "FLASK_SECRET_KEY must be configured."
        )

    app.secret_key = "site-sensei-development-only"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RUBRICS_DIR = os.path.join(os.path.dirname(__file__), "rubrics")


def get_teacher_password():
    """Return the configured teacher password, or None when teacher mode is disabled."""
    return os.getenv('TEACHER_PASSWORD') or None


def teacher_mode_unavailable():
    return render_template('teacher_unavailable.html'), 503


def get_server_config():
    """Return Flask bind settings from the local or container environment."""
    debug = os.getenv('FLASK_DEBUG', '').lower() in {'1', 'true', 'yes'}
    return {
        'host': os.getenv('FLASK_HOST', '0.0.0.0'),
        'port': int(os.getenv('PORT', '5000')),
        'debug': debug,
    }


# 🔐 New login route
@app.route('/teacher', methods=['GET', 'POST'])
def teacher_login():
    teacher_password = get_teacher_password()
    if teacher_password is None:
        return teacher_mode_unavailable()

    if request.method == 'POST':
        password = request.form.get('password')
        if password == teacher_password:
            return redirect(url_for('teacher_batch'))
        else:
            flash('Incorrect password. Try again.')
    return render_template('teacher_login.html')


@app.route('/teacher-batch', methods=['GET', 'POST'])
def teacher_batch():
    if get_teacher_password() is None:
        return teacher_mode_unavailable()

    if request.method == 'POST':
        uploaded_file = request.files.get('csv_file')
        sheet_link = request.form.get('sheet_link')
        input_csv_path = os.path.join(DATA_DIR, 'student_pages.csv')

        if uploaded_file and uploaded_file.filename:
            uploaded_file.save(input_csv_path)
        elif sheet_link:
            try:
                response = requests.get(sheet_link, timeout=DEFAULT_REQUEST_TIMEOUT)
                with open(input_csv_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
            except Exception as e:
                return f"❌ Failed to download Google Sheet: {e}"

        # Run the batch grader
        output_csv = os.path.join(DATA_DIR, 'grades_output.csv')
        output_html = os.path.join(DATA_DIR, 'grades_feedback.html')
        try:
            grade_from_csv(input_csv_path, output_csv, output_html)
        except Exception as e:
            return f"❌ Error during grading: {e}"

        return redirect(url_for('teacher_results'))

    return render_template('teacher_upload.html')


@app.route('/teacher-results')
def teacher_results():
    if get_teacher_password() is None:
        return teacher_mode_unavailable()
    return render_template('teacher_results.html')


@app.route('/download/csv')
def download_csv():
    if get_teacher_password() is None:
        return teacher_mode_unavailable()
    return send_file(os.path.join(DATA_DIR, 'grades_output.csv'), as_attachment=True)


@app.route('/download/html')
def download_html():
    if get_teacher_password() is None:
        return teacher_mode_unavailable()
    return send_file(os.path.join(DATA_DIR, 'grades_feedback.html'), as_attachment=False)

@app.route('/student', methods=['GET', 'POST'])
def student_upload():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()

        if not url:
            flash('Please enter a project URL.')
            return render_template('student_upload.html', submitted_url=url)

        try:
            feedback_html = generate_feedback_html(url)

            return render_template(
                'student_results.html',
                submitted_url=url,
                feedback_html=feedback_html,
            )

        except Exception as e:
            flash(f'Unable to grade webpage: {e}')
            return render_template('student_upload.html', submitted_url=url)

    return render_template('student_upload.html')


@app.route('/rubrics/html-mini-web-page-rubric.pdf')
def example_rubric():
    return send_from_directory(
        RUBRICS_DIR,
        'html-mini-web-page-rubric.pdf',
        mimetype='application/pdf',
    )


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(**get_server_config())
