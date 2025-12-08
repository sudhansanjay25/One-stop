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
	"""Header with logo placeholder and institution details."""
	top = height - 15 * mm
	left = 20 * mm
	
	c.setFillColor(colors.black)
	c.setStrokeColor(colors.black)
	c.setLineWidth(1)
	
	# Logo placeholder box on left
	logo_size = 28 * mm
	c.rect(left, top - logo_size, logo_size, logo_size)
	c.setFont("Helvetica", 8)
	c.drawCentredString(left + logo_size/2, top - logo_size/2, "LOGO")
	
	# Institution name and details (centered)
	header_x = width / 2
	c.setFont("Helvetica-Bold", 14)
	c.drawCentredString(header_x, top - 5 * mm, "SRI SHAKTHI INSTITUTE OF ENGINEERING AND TECHNOLOGY")
	c.setFont("Helvetica", 9)
	c.drawCentredString(header_x, top - 10 * mm, "COIMBATORE - R2")
	c.setFont("Helvetica", 8)
	c.drawCentredString(header_x, top - 14 * mm, "[An Autonomous Institution]")
	c.setFont("Helvetica-Bold", 11)
	c.drawCentredString(header_x, top - 20 * mm, "OFFICE OF THE CONTROLLER OF EXAMINATIONS")
	c.setFont("Helvetica-Bold", 12)
	c.drawCentredString(header_x, top - 26 * mm, "HALL TICKET")
	c.setFont("Helvetica", 10)
	c.drawCentredString(header_x, top - 31 * mm, "END SEMESTER EXAMINATIONS - APR 2025")


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

	# Main info box with border
	left = 20 * mm
	right = width - 20 * mm
	box_top = height - 55 * mm
	box_height = 28 * mm
	
	c.setStrokeColor(colors.black)
	c.setLineWidth(1.2)
	c.rect(left, box_top - box_height, right - left, box_height)
	
	# Photo box in top right corner of info box
	photo_w = 25 * mm
	photo_h = 28 * mm
	c.rect(right - photo_w, box_top - box_height, photo_w, photo_h)
	c.setFont("Helvetica", 8)
	c.drawCentredString(right - photo_w/2, box_top - box_height/2, "Photo")
	
	# Info rows inside box
	info_left = left + 3 * mm
	y = box_top - 7 * mm
	
	# Row 1: Name and Register Number
	c.setFont("Helvetica-Bold", 9)
	c.drawString(info_left, y, "Name:")
	c.setFont("Helvetica", 9)
	c.drawString(info_left + 15 * mm, y, p["name"].upper())
	c.setFont("Helvetica-Bold", 9)
	c.drawString(info_left + 95 * mm, y, "Register Number:")
	c.setFont("Helvetica", 9)
	c.drawString(info_left + 135 * mm, y, p["reg_id"])
	
	# Row 2: Degree & Branch (full width)
	y -= 7 * mm
	c.setFont("Helvetica-Bold", 9)
	c.drawString(info_left, y, "Degree & Branch:")
	c.setFont("Helvetica", 9)
	c.drawString(info_left + 30 * mm, y, "B.Tech . ARTIFICIAL INTELLIGENCE AND DATA SCIENCE")
	
	# Row 3: Date of Birth, Semester, Gender, Regulation
	y -= 7 * mm
	c.setFont("Helvetica-Bold", 9)
	c.drawString(info_left, y, "Date of Birth:")
	c.setFont("Helvetica", 9)
	c.drawString(info_left + 25 * mm, y, "25.09.2005")
	c.setFont("Helvetica-Bold", 9)
	c.drawString(info_left + 55 * mm, y, "Semester:")
	c.setFont("Helvetica", 9)
	c.drawString(info_left + 72 * mm, y, "4")
	c.setFont("Helvetica-Bold", 9)
	c.drawString(info_left + 85 * mm, y, "Gender:")
	c.setFont("Helvetica", 9)
	c.drawString(info_left + 100 * mm, y, "MALE")
	c.setFont("Helvetica-Bold", 9)
	c.drawString(info_left + 120 * mm, y, "Regulation:")
	c.setFont("Helvetica", 9)
	c.drawString(info_left + 142 * mm, y, "2021")

	# Exam schedule table
	table_top = box_top - box_height - 8 * mm
	table_left = left
	table_width = right - left
	row_height = 7 * mm
	
	# Table header with borders
	c.setStrokeColor(colors.black)
	c.setLineWidth(0.5)
	y = table_top
	
	# Column widths
	col_sem = 10 * mm
	col_date = 25 * mm
	col_session = 20 * mm
	col_code = 25 * mm
	col_name = table_width - col_sem - col_date - col_session - col_code
	
	# Header row
	c.setFont("Helvetica-Bold", 9)
	c.rect(table_left, y - row_height, col_sem, row_height)
	c.drawString(table_left + 2 * mm, y - row_height + 2 * mm, "Sem")
	
	c.rect(table_left + col_sem, y - row_height, col_date, row_height)
	c.drawString(table_left + col_sem + 2 * mm, y - row_height + 2 * mm, "Date")
	
	c.rect(table_left + col_sem + col_date, y - row_height, col_session, row_height)
	c.drawString(table_left + col_sem + col_date + 2 * mm, y - row_height + 2 * mm, "Session")
	
	c.rect(table_left + col_sem + col_date + col_session, y - row_height, col_code, row_height)
	c.drawString(table_left + col_sem + col_date + col_session + 2 * mm, y - row_height + 2 * mm, "Subject Code")
	
	c.rect(table_left + col_sem + col_date + col_session + col_code, y - row_height, col_name, row_height)
	c.drawString(table_left + col_sem + col_date + col_session + col_code + 2 * mm, y - row_height + 2 * mm, "Subject Name")
	
	# Data rows (11 empty rows)
	y -= row_height
	c.setFont("Helvetica", 9)
	for i in range(11):
		c.rect(table_left, y - row_height, col_sem, row_height)
		c.rect(table_left + col_sem, y - row_height, col_date, row_height)
		c.rect(table_left + col_sem + col_date, y - row_height, col_session, row_height)
		c.rect(table_left + col_sem + col_date + col_session, y - row_height, col_code, row_height)
		c.rect(table_left + col_sem + col_date + col_session + col_code, y - row_height, col_name, row_height)
		y -= row_height
	
	# Total subjects registered
	y -= 5 * mm
	c.setFont("Helvetica-Bold", 9)
	c.drawString(table_left, y, "Total Number of Subjects Registered: 11")

	# Signatures at bottom
	y -= 30 * mm
	sig_y = y
	
	# Candidate signature line
	c.setLineWidth(0.5)
	c.line(table_left, sig_y, table_left + 40 * mm, sig_y)
	c.setFont("Helvetica", 8)
	c.drawString(table_left, sig_y - 4 * mm, "Candidate Signature")
	
	# Controller signature line
	controller_x = table_left + 65 * mm
	c.line(controller_x, sig_y, controller_x + 40 * mm, sig_y)
	c.drawString(controller_x, sig_y - 4 * mm, "Controller of Examinations")
	
	# Principal signature line  
	principal_x = controller_x + 60 * mm
	c.line(principal_x, sig_y, principal_x + 30 * mm, sig_y)
	c.drawString(principal_x, sig_y - 4 * mm, "Principal")
	
	# Seal circle on bottom right
	seal_x = right - 20 * mm
	seal_y = sig_y - 10 * mm
	c.setLineWidth(1)
	c.circle(seal_x, seal_y, 15 * mm)
	c.setFont("Helvetica", 8)
	c.drawCentredString(seal_x, seal_y, "SEAL")

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
