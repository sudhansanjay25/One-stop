import pdfkit
from jinja2 import Environment, FileSystemLoader
import os

# Configure wkhtmltopdf path - update this to your installation path
# Common paths:
# Windows: r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# Linux: '/usr/local/bin/wkhtmltopdf'
config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

# Single mock student data
students = [
    {
        "name": "SUDHAN SANJAY V P",
        "reg_no": "714023243152",
        "dob": "25.09.2005"
    }
]

# Hall ticket configuration
branch = "ARTIFICIAL INTELLIGENCE AND DATA SCIENCE"
semester = "4"
gender = "MALE"
regulation = "2021"

# Subjects with complete details matching the template
subjects = [
    {"sem": "4", "date": "04.06.2025", "session": "FN", "code": "21MA405", "name": "Probability, Statistics and Queuing Theory"},
    {"sem": "4", "date": "02.06.2025", "session": "FN", "code": "21CS401", "name": "Design and Analysis of Algorithms"},
    {"sem": "4", "date": "31.05.2025", "session": "FN", "code": "21AD401", "name": "Machine Learning"},
    {"sem": "4", "date": "24.05.2025", "session": "FN", "code": "21AD402", "name": "Big Data Management"},
    {"sem": "4", "date": "19.05.2025", "session": "FN", "code": "21CS421", "name": "Advanced Databases"},
    {"sem": "4", "date": "21.05.2025", "session": "FN", "code": "21AM422", "name": "JAVA Programming"},
    {"sem": "4", "date": "", "session": "", "code": "21AD411", "name": "Engineering Exploration.IV"},
    {"sem": "4", "date": "", "session": "", "code": "21CS412", "name": "Design and Analysis of Algorithms Laboratory"},
    {"sem": "4", "date": "", "session": "", "code": "21AD412", "name": "Machine Learning Laboratory"},
    {"sem": "4", "date": "", "session": "", "code": "21AG413", "name": "General Agri Business Management"},
    {"sem": "4", "date": "", "session": "", "code": "21EM401", "name": "Career Enhancement Program . II"}
]

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("hall_ticket.html")

os.makedirs("output", exist_ok=True)

for student in students:
    html = template.render(
        branch=branch,
        semester=semester,
        gender=gender,
        regulation=regulation,
        subjects=subjects,
        student=student
    )

    pdf_path = f"output/{student['reg_no']}_hallticket.pdf"
    pdfkit.from_string(html, pdf_path, configuration=config)

    print("Generated:", pdf_path)
