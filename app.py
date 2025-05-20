from flask import Flask, request, render_template, send_file, redirect, url_for
from teacher_mode.batch_grader import grade_from_csv
import requests
import os

app = Flask(__name__)
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


@app.route('/teacher-batch', methods=['GET', 'POST'])
def teacher_batch():
    if request.method == 'POST':
        uploaded_file = request.files.get('csv_file')
        sheet_link = request.form.get('sheet_link')
        input_csv_path = os.path.join(DATA_DIR, 'student_pages.csv')

        if uploaded_file and uploaded_file.filename:
            uploaded_file.save(input_csv_path)
        elif sheet_link:
            try:
                response = requests.get(sheet_link)
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
    return render_template('teacher_results.html')


@app.route('/download/csv')
def download_csv():
    return send_file(os.path.join(DATA_DIR, 'grades_output.csv'), as_attachment=True)


@app.route('/download/html')
def download_html():
    return send_file(os.path.join(DATA_DIR, 'grades_feedback.html'), as_attachment=False)

@app.route('/')
def home():
    return '''
    <h1>Welcome to SiteSensei</h1>
    <p>Select your mode:</p>
    <a href="/student-check"><button>👩‍🎓 I'm a Student</button></a>
    <a href="/teacher-batch"><button>👨‍🏫 I'm a Teacher</button></a>
    '''


if __name__ == '__main__':
    app.run(debug=True)
