import os
import socket
from flask import Flask, send_from_directory, render_template_string, url_for, redirect
import qrcode
import io
import base64

app = Flask(__name__)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

QR_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Hall Ticket Download QR</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 30px; }
    .wrap { max-width: 600px; margin: 0 auto; text-align: center; }
    img { width: 280px; height: 280px; }
    .hint { margin-top: 14px; color: #444; }
    code { background: #f4f4f4; padding: 2px 6px; }
  </style>
</head>
<body>
  <div class="wrap">
    <h2>Scan to Download Hall Ticket</h2>
    <p>Point your phone camera at the QR below.</p>
    <img src="data:image/png;base64,{{ qr_b64 }}" alt="Download QR">
    <div class="hint">
      If scanning on the same laptop, open <code>{{ download_url }}</code> in a browser.
    </div>
    <p><a href="{{ download_url }}">Direct download link</a></p>
  </div>
</body>
</html>
"""


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

@app.route('/')
def index():
    # Redirect to QR for first available PDF
    files = [f for f in os.listdir(OUTPUT_DIR) if f.lower().endswith('.pdf')]
    if not files:
        return 'No PDFs found in output/. Please run generate.py first.', 404
    return redirect(url_for('qr_for', filename=files[0]))

@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

@app.route('/qr/<path:filename>')
def qr_for(filename):
    ip = get_local_ip()
    # Build absolute URL for download
    download_url = f"http://{ip}:5000/download/{filename}"
    # Create QR image
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(download_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    return render_template_string(QR_TEMPLATE, qr_b64=qr_b64, download_url=download_url)

if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
