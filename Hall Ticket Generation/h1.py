"""
Hall Ticket Generator (PDF only)

Generates PDF hall tickets for mock participants (no QR in PDF).

Usage (Windows cmd):
  1) Install deps:
	 pip install reportlab
  2) Run:
	 python "Hall Ticket Generation\\h1.py"

Outputs PDF files under ./Hall Ticket Generation/output/
"""

import os
from datetime import datetime
from typing import List, Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph


# --------------------------
# Configuration
# --------------------------
EVENT_NAME = "One-Stop Hackathon"
EVENT_DATE = "Dec 14–15, 2025"
EVENT_VENUE = "Tech Convention Center, Bengaluru"
ORG_NAME = "Hackathon Committee"

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def ensure_output_dir() -> str:
	os.makedirs(OUTPUT_DIR, exist_ok=True)
	return OUTPUT_DIR


def make_mock_participants(n: int = 10) -> List[Dict]:
	"""Create mock participant data."""
	tracks = ["AI/ML", "Web", "Mobile", "Data", "IoT"]
	colleges = [
		"Tech Institute of India",
		"Global Engineering College",
		"City University",
		"National Institute of Technology",
		"Regional College of Engineering",
	]
	participants: List[Dict] = []
	for i in range(1, n + 1):
		reg_id = f"HACK-{datetime.now().strftime('%Y%m%d')}-{i:03d}"
		participants.append(
			{
				"name": f"Participant {i}",
				"college": colleges[i % len(colleges)],
				"email": f"participant{i}@example.com",
				"phone": f"9{str(100000000 + i).zfill(9)}",
				"track": tracks[i % len(tracks)],
				"reg_id": reg_id,
				"team": f"Team-{(i-1)//3 + 1}",
			}
		)
	return participants




def draw_header(c: canvas.Canvas, width: float, height: float):
	"""Structured header similar to the provided hall ticket format."""
	top = height - 20 * mm
	c.setFillColor(colors.black)
	c.setStrokeColor(colors.black)
	c.setLineWidth(1.2)

	c.setFont("Helvetica-Bold", 16)
	c.drawCentredString(width / 2, top, "SRI SHAKTHI INSTITUTE OF ENGINEERING AND TECHNOLOGY")
	c.setFont("Helvetica", 10)
	c.drawCentredString(width / 2, top - 6 * mm, "COIMBATORE - R2   [An Autonomous Institution]")
	c.setFont("Helvetica-Bold", 12)
	c.drawCentredString(width / 2, top - 13 * mm, "OFFICE OF THE CONTROLLER OF EXAMINATIONS")
	c.setFont("Helvetica-Bold", 12)
	c.drawCentredString(width / 2, top - 20 * mm, "HALL TICKET")
	c.setFont("Helvetica", 11)
	c.drawCentredString(width / 2, top - 26 * mm, "END SEMESTER EXAMINATIONS - APR 2025")
	c.line(15 * mm, top - 30 * mm, width - 15 * mm, top - 30 * mm)


def draw_footer(c: canvas.Canvas, width: float):
	c.setFont("Helvetica", 9)
	c.setFillColor(colors.HexColor("#666666"))
	c.drawString(20 * mm, 15 * mm, "Please carry a valid ID card. QR code required for entry.")
	c.drawRightString(width - 20 * mm, 15 * mm, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


def render_hall_ticket(p: Dict, out_path: str):
	"""Render a single PDF hall ticket for participant p."""
	width, height = A4
	c = canvas.Canvas(out_path, pagesize=A4)

	# Header
	draw_header(c, width, height)

	# Candidate detail grid and photo placeholder
	left = 15 * mm
	right = width - 15 * mm
	y = height - 80 * mm
	row_h = 10 * mm

	# Photo box on the right
	photo_w = 25 * mm
	photo_h = 30 * mm
	c.rect(right - photo_w, y - photo_h + 5 * mm, photo_w, photo_h)
	c.setFont("Helvetica", 8)
	c.drawCentredString(right - photo_w/2, y - photo_h/2 + 5 * mm, "Photo")

	# Name
	c.setFont("Helvetica-Bold", 10)
	c.drawString(left, y, "Name:")
	c.setFont("Helvetica", 10)
	c.drawString(left + 30 * mm, y, p["name"])
	# Register Number
	y -= row_h
	c.setFont("Helvetica-Bold", 10)
	c.drawString(left, y, "Register Number:")
	c.setFont("Helvetica", 10)
	c.drawString(left + 30 * mm, y, p["reg_id"])
	# Degree & Branch
	y -= row_h
	c.setFont("Helvetica-Bold", 10)
	c.drawString(left, y, "Degree & Branch:")
	c.setFont("Helvetica", 10)
	c.drawString(left + 30 * mm, y, "B.Tech . ARTIFICIAL INTELLIGENCE AND DATA SCIENCE")
	# DOB, Semester
	y -= row_h
	c.setFont("Helvetica-Bold", 10)
	c.drawString(left, y, "Date of Birth:")
	c.setFont("Helvetica", 10)
	c.drawString(left + 30 * mm, y, "")
	c.setFont("Helvetica-Bold", 10)
	c.drawString(left + 85 * mm, y, "Semester:")
	c.setFont("Helvetica", 10)
	c.drawString(left + 115 * mm, y, "")
	# Gender, Regulation
	y -= row_h
	c.setFont("Helvetica-Bold", 10)
	c.drawString(left, y, "Gender:")
	c.setFont("Helvetica", 10)
	c.drawString(left + 30 * mm, y, "")
	c.setFont("Helvetica-Bold", 10)
	c.drawString(left + 85 * mm, y, "Regulation:")
	c.setFont("Helvetica", 10)
	c.drawString(left + 115 * mm, y, "")

	# Schedule table header
	y -= 15 * mm
	c.setFont("Helvetica-Bold", 11)
	c.drawString(left, y, "Sem")
	c.drawString(left + 12 * mm, y, "Date")
	c.drawString(left + 45 * mm, y, "Session")
	c.drawString(left + 70 * mm, y, "Subject Code")
	c.drawString(left + 110 * mm, y, "Subject Name")
	c.line(left, y - 2 * mm, right, y - 2 * mm)

	# Placeholder rows
	y -= 8 * mm
	c.setFont("Helvetica", 10)
	for _ in range(11):
		c.setStrokeColor(colors.HexColor("#aaaaaa"))
		c.line(left, y + 3 * mm, right, y + 3 * mm)
		c.setStrokeColor(colors.black)
		y -= 8 * mm

	# Total subjects
	y -= 5 * mm
	c.setFont("Helvetica-Bold", 10)
	c.drawString(left, y, "Total Number of Subjects Registered: ")
	c.setFont("Helvetica", 10)
	c.drawString(left + 80 * mm, y, "")

	# Footer signatures and seal
	y -= 25 * mm
	sig_y = y
	c.line(left, sig_y, left + 45 * mm, sig_y)
	c.setFont("Helvetica", 9)
	c.drawString(left, sig_y - 5 * mm, "Candidate Signature")
	c.line(left + 60 * mm, sig_y, left + 105 * mm, sig_y)
	c.drawString(left + 60 * mm, sig_y - 5 * mm, "Controller of Examinations")
	c.line(left + 120 * mm, sig_y, left + 165 * mm, sig_y)
	c.drawString(left + 120 * mm, sig_y - 5 * mm, "Principal")
	seal_x = right - 25 * mm
	seal_y = sig_y - 5 * mm
	c.circle(seal_x, seal_y, 12 * mm)
	c.setFont("Helvetica", 8)
	c.drawCentredString(seal_x, seal_y, "SEAL")

	# No QR on the hall ticket; portal will display QR separately for download

	# Instruction note (centered under header area)
	styles = getSampleStyleSheet()
	style = styles["Normal"]
	style.fontName = "Helvetica"
	style.fontSize = 9
	style.leading = 12
	text = (
		"Carry a valid ID card. Be present at least 15 minutes before the session. "
		"Electronic gadgets are strictly prohibited inside the exam hall."
	)
	para = Paragraph(text, style)
	para.wrapOn(c, width - 30 * mm, 30 * mm)
	para.drawOn(c, 15 * mm, height - 98 * mm)
	

	# Footer
	draw_footer(c, width)

	c.showPage()
	c.save()


def generate_all(n: int = 1) -> List[str]:
	ensure_output_dir()
	participants = make_mock_participants(n)
	out_files: List[str] = []
	for p in participants:
		filename = f"{p['reg_id']}_{p['name'].replace(' ', '_')}.pdf"
		out_path = os.path.join(OUTPUT_DIR, filename)
		render_hall_ticket(p, out_path)
		out_files.append(out_path)
	return out_files


def main():
	print("Generating hall tickets with QR codes...")
	out_files = generate_all(n=1)
	print(f"Done. Generated {len(out_files)} files in: {OUTPUT_DIR}")
	for f in out_files[:3]:
		print(" -", f)


if __name__ == "__main__":
	main()
