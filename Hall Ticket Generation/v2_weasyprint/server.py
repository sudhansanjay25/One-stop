import os
import socket
import sqlite3
import io
import base64
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, make_response, send_file
from jinja2 import Environment, FileSystemLoader
import qrcode
import pdfkit

app = Flask(__name__)
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
DB_PATH = Path(__file__).with_name('students.db')

# Configure wkhtmltopdf path (update if installed elsewhere)
WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
try:
    PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
except Exception:
    PDFKIT_CONFIG = None

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def get_local_ip():
    """Get local IP address for QR code URLs"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def fetch_student_and_subjects(reg_no):
    """Fetch student details and subjects from database"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Fetch student info
    cur.execute('''
        SELECT reg_no, name, deg, branch, dob, sem, gender, semtime, regulation 
        FROM students WHERE reg_no=?
    ''', (reg_no,))
    row = cur.fetchone()
    
    if not row:
        conn.close()
        return None
    
    student = {
        'reg_no': row[0],
        'name': row[1],
        'deg': row[2],
        'branch': row[3],
        'dob': row[4],
        'sem': row[5],
        'gender': row[6],
        'semtime': row[7],
        'regulation': row[8] if len(row) > 8 else '2015'
    }
    
    # Fetch subjects
    cur.execute('''
        SELECT sem, date, session, code, name 
        FROM subjects WHERE reg_no=? ORDER BY sem, code
    ''', (reg_no,))
    subjects = [
        {
            'sem': r[0],
            'date': r[1],
            'session': r[2],
            'code': r[3],
            'name': r[4]
        }
        for r in cur.fetchall()
    ]
    
    conn.close()
    return student, subjects


def generate_qr_base64(url):
    """Generate QR code as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.read()).decode()


def generate_hall_ticket_pdf(reg_no):
    """Generate hall ticket PDF using WeasyPrint"""
    # Fetch data
    data = fetch_student_and_subjects(reg_no)
    if data is None:
        return None
    
    student, subjects = data
    
    # Generate QR code pointing to verification page
    ip = get_local_ip()
    verify_url = f"http://{ip}:5000/verify/{reg_no}"
    qr_base64 = generate_qr_base64(verify_url)
    
    # Prepare context for template
    context = {
        'name': student['name'],
        'reg_no': student['reg_no'],
        'deg': student['deg'],
        'branch': student['branch'],
        'dob': student['dob'],
        'sem': student['sem'],
        'gender': student['gender'],
        'semtime': student['semtime'],
        'regulation': student.get('regulation', '2015'),
        'subjects': subjects,
        'qr_base64': qr_base64
    }
    
    # Render HTML template
    template = env.get_template('hall_ticket_template.html')
    html_content = template.render(context)
    
    # Convert HTML to PDF using pdfkit
    if PDFKIT_CONFIG is None:
        raise RuntimeError('wkhtmltopdf not found. Please install from: https://wkhtmltopdf.org/downloads.html')
    
    pdf_bytes = pdfkit.from_string(html_content, False, configuration=PDFKIT_CONFIG, options={
        'enable-local-file-access': None,
        'quiet': ''
    })
    
    return io.BytesIO(pdf_bytes)


@app.route('/')
def index():
    """Landing page with register number input form"""
    return render_template('index.html')


@app.route('/qr')
def show_qr():
    """Display QR code page for a specific register number"""
    reg_no = request.args.get('reg_no')
    if not reg_no:
        return redirect(url_for('index'))
    
    # Verify student exists
    data = fetch_student_and_subjects(reg_no)
    if data is None:
        return f"<h2>Student with Register Number '{reg_no}' not found!</h2><br><a href='/'>Go Back</a>", 404
    
    student, _ = data
    
    # Generate QR code for download link
    ip = get_local_ip()
    download_url = f"http://{ip}:5000/download/{reg_no}"
    qr_base64 = generate_qr_base64(download_url)
    
    return render_template('qr_page.html', 
                         reg_no=reg_no,
                         name=student['name'],
                         qr_base64=qr_base64,
                         download_url=download_url)


@app.route('/download/<reg_no>')
def download_hall_ticket(reg_no):
    """Generate and stream PDF hall ticket"""
    try:
        pdf_buffer = generate_hall_ticket_pdf(reg_no)
        if pdf_buffer is None:
            return f"<h2>Student with Register Number '{reg_no}' not found!</h2>", 404
        
        pdf_buffer.seek(0)
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{reg_no}_hall_ticket.pdf'
        )
    except Exception as e:
        return f"<h2>Error generating hall ticket: {str(e)}</h2><br><a href='/'>Go Back</a>", 500


@app.route('/verify/<reg_no>')
def verify_student(reg_no):
    """Mock verification website (scanned from QR code)"""
    data = fetch_student_and_subjects(reg_no)
    if data is None:
        return f"<h2>Invalid Hall Ticket</h2><p>Register Number '{reg_no}' not found in database.</p>", 404
    
    student, subjects = data
    
    return render_template('verify.html',
                         reg_no=student['reg_no'],
                         name=student['name'],
                         branch=student['branch'],
                         degree=student['deg'],
                         semester=student['sem'])


if __name__ == '__main__':
    if not DB_PATH.exists():
        print("=" * 60)
        print("ERROR: Database not found!")
        print(f"Please run: python db_setup.py")
        print("=" * 60)
    else:
        ip = get_local_ip()
        print("=" * 60)
        print(f"Hall Ticket Generation System")
        print(f"Server running at: http://{ip}:5000")
        print(f"Local access: http://localhost:5000")
        print("=" * 60)
        app.run(host='0.0.0.0', port=5000, debug=True)
