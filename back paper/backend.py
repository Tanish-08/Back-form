from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configure upload folder and allowed file extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Database file
DATABASE = 'examination_form.db'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ensure database exists
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                department TEXT,
                name TEXT,
                father_name TEXT,
                enroll_no TEXT,
                program_name TEXT,
                semester_batch TEXT,
                email TEXT,
                fee_receipt_no TEXT,
                amount TEXT,
                fee_receipt_file TEXT,
                form_type TEXT,
                courses TEXT,
                signature_file TEXT,
                submission_date TEXT
            )
        ''')
        conn.commit()

init_db()

# Helper function to validate uploaded files
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to display the form (optional, for debugging)
@app.route('/')
def form():
    return render_template('index.html')  # Save the HTML file as `templates/index.html`

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        # Retrieve personal information
        department = request.form.get('department')
        name = request.form.get('name')
        father_name = request.form.get('father_name')
        enroll_no = request.form.get('enroll_no.')
        program_name = request.form.get('program_name')
        semester_batch = request.form.get('semester_batch')
        email = request.form.get('email')
        fee_receipt_no = request.form.get('fee_receipt_no')
        amount = request.form.get('amount')

        # Handle fee receipt file upload
        fee_receipt_file = request.files.get('fee_receipt_file')
        fee_receipt_filename = None
        if fee_receipt_file and allowed_file(fee_receipt_file.filename):
            fee_receipt_filename = secure_filename(fee_receipt_file.filename)
            fee_receipt_file.save(os.path.join(app.config['UPLOAD_FOLDER'], fee_receipt_filename))

        # Determine form type (back paper or repeat course)
        form_type = request.form.getlist('formSection')

        # Collect course details
        courses = []
        if 'back' in form_type:
            courses.extend(zip(
                request.form.getlist('back_semester[]'),
                request.form.getlist('back_course_code[]'),
                request.form.getlist('back_course_name[]')
            ))
        if 'repeat' in form_type:
            courses.extend(zip(
                request.form.getlist('repeat_semester[]'),
                request.form.getlist('repeat_course_code[]'),
                request.form.getlist('repeat_course_name[]')
            ))

        # Handle student signature upload
        signature_file = request.files.get('student_signature')
        signature_filename = None
        if signature_file and allowed_file(signature_file.filename):
            signature_filename = secure_filename(signature_file.filename)
            signature_file.save(os.path.join(app.config['UPLOAD_FOLDER'], signature_filename))

        # Save form data to database
        submission_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO submissions (
                    department, name, father_name, enroll_no, program_name,
                    semester_batch, email, fee_receipt_no, amount,
                    fee_receipt_file, form_type, courses, signature_file, submission_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                department, name, father_name, enroll_no, program_name,
                semester_batch, email, fee_receipt_no, amount,
                fee_receipt_filename, ','.join(form_type), str(courses), signature_filename, submission_date
            ))
            conn.commit()

        return jsonify({"message": "Form submitted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to list all submissions (for admin view)
@app.route('/submissions', methods=['GET'])
def list_submissions():
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM submissions')
            rows = cursor.fetchall()
            submissions = [
                {
                    "id": row[0],
                    "department": row[1],
                    "name": row[2],
                    "father_name": row[3],
                    "enroll_no": row[4],
                    "program_name": row[5],
                    "semester_batch": row[6],
                    "email": row[7],
                    "fee_receipt_no": row[8],
                    "amount": row[9],
                    "fee_receipt_file": row[10],
                    "form_type": row[11],
                    "courses": row[12],
                    "signature_file": row[13],
                    "submission_date": row[14],
                }
                for row in rows
            ]
        return jsonify(submissions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
