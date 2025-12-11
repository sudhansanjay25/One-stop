# HALL TICKET GENERATION SYSTEM - v2 (WeasyPrint)

## Quick Start Guide

### 1. Activate Virtual Environment
```cmd
cd "c:\Users\Lenovo\Desktop\Project\One-Stop-Hackathon\Hall Ticket Generation\v2_weasyprint"
..\ht\Scripts\activate
```

### 2. Install Required Packages
```cmd
pip install Flask
pip install WeasyPrint
pip install qrcode[pil]
pip install Jinja2
pip install Pillow
```

### 3. Initialize Database
```cmd
python db_setup.py
```

### 4. Run Server
```cmd
python server.py
```

### 5. Access the System
- Open browser: `http://localhost:5000`
- Or from mobile on same network: `http://YOUR_LOCAL_IP:5000`

---

## System Architecture

```
v2_weasyprint/
├── server.py                           # Flask application
├── db_setup.py                         # Database initialization script
├── students.db                         # SQLite database (created after setup)
└── templates/
    ├── index.html                      # Register number input form
    ├── qr_page.html                    # QR code display page
    ├── hall_ticket_template.html       # PDF generation template
    └── verify.html                     # Mock verification website
```

---

## Features

✅ **HTML-to-PDF Conversion**: No Word or LibreOffice required
✅ **Automatic Overflow Handling**: Long subject lists span multiple pages
✅ **QR Code Integration**: Embedded in PDF, points to verification page
✅ **Mock Verification Site**: Simple webpage showing student details
✅ **Clean Layout**: Exact replica of reference image (no photos, no signatures)
✅ **Fast Generation**: 1-2 seconds per PDF
✅ **No File Storage**: PDFs generated on-demand and streamed

---

## Sample Register Numbers

### Computer Science (CSE)
- CSE001, CSE002, CSE003, CSE004, CSE005, CSE006, CSE007

### Electronics (ECE) - 35+ subjects to test overflow
- ECE001, ECE002, ECE003, ECE004, ECE005, ECE006, ECE007

### Mechanical (MECH)
- MECH001, MECH002, MECH003, MECH004, MECH005, MECH006

---

## How It Works

1. **User enters register number** → `http://localhost:5000`
2. **System shows QR code** → `http://localhost:5000/qr?reg_no=CSE001`
3. **User scans QR or clicks link** → Triggers PDF generation
4. **PDF downloads instantly** → `http://localhost:5000/download/CSE001`
5. **QR in PDF links to verification** → `http://localhost:5000/verify/CSE001`

---

## Customization

### Edit Hall Ticket Layout
Open `templates/hall_ticket_template.html` and modify:
- CSS styles in `<style>` section
- HTML structure in `<body>` section
- No Python coding required!

### Add More Students
Edit `db_setup.py`:
- Modify `STUDENTS` list
- Add subjects to `SUBJECTS_BY_DEPT`
- Run `python db_setup.py` again

---

## Troubleshooting

### WeasyPrint Installation Issues (Windows)
If WeasyPrint fails to install:
```cmd
pip install --upgrade pip
pip install WeasyPrint --no-cache-dir
```

If still fails, install GTK+ for Windows:
- Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
- Or use fallback: `pip install pdfkit` (requires wkhtmltopdf)

### Database Not Found Error
Run: `python db_setup.py`

### QR Code Not Working on Mobile
- Ensure phone and PC are on same Wi-Fi
- Use the local IP address displayed in server startup
- Some corporate networks block peer-to-peer connections

---

## Testing Checklist

- [ ] Enter CSE001 → Check PDF with 5 subjects
- [ ] Enter ECE001 → Check PDF spans multiple pages (35+ subjects)
- [ ] Scan QR code from phone → Verify download works
- [ ] Click QR in PDF → Verify mock website loads
- [ ] Test with invalid register number → Check error handling

---

## Production Deployment Notes

For actual server deployment:
1. Replace `get_local_ip()` with actual domain name
2. Use HTTPS for QR codes to work reliably
3. Add authentication if needed
4. Consider caching PDFs for bulk downloads
5. Add photo integration by extending database schema

---

## Differences from v1

| Feature | v1 (DOCX) | v2 (WeasyPrint) |
|---------|-----------|-----------------|
| Template | Word .docx | HTML + CSS |
| Dependencies | Word/LibreOffice | Pure Python |
| Overflow | Manual/breaks | Automatic pagination |
| Speed | Slow (COM) | Fast (direct) |
| Customization | Edit .docx | Edit HTML/CSS |
| Server-ready | No | Yes |

---

## Support

If you encounter issues:
1. Check terminal for error messages
2. Verify all packages installed: `pip list`
3. Ensure database exists: `ls students.db` or `dir students.db`
4. Check Flask logs for detailed errors

---

**System ready for testing!** 🚀
