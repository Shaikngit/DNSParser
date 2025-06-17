from flask import Flask, render_template_string, request, send_file, redirect, url_for, flash
import pandas as pd
import dnslib
import binascii
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'dnsparser_secret_key'
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

INFO_TEXT = """
<h2>DNS Packet Parser Tool</h2>
<p>This tool allows you to upload an Excel or CSV file containing DNS packet data. It will parse the <b>PacketData</b> column using dnslib and return a new file with an additional column containing the parsed DNS data.</p>
<ul>
  <li>Supported formats: .xlsx, .xls, .csv</li>
  <li>The file must contain a <b>PacketData</b> column.</li>
</ul>
"""

HTML_TEMPLATE = """
<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>DNS Packet Parser Tool</title>
  <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css' rel='stylesheet'>
  <style>
    body { background: #f8fafc; }
    .main-card { margin-top: 40px; box-shadow: 0 2px 16px rgba(0,0,0,0.07); }
    .footer { margin-top: 40px; color: #888; font-size: 0.95em; text-align: center; }
    .logo { font-weight: bold; color: #0078d4; letter-spacing: 1px; }
    .msg-success { color: #198754; }
    .msg-error { color: #dc3545; }
  </style>
</head>
<body>
  <div class='container'>
    <div class='row justify-content-center'>
      <div class='col-md-8'>
        <div class='card main-card'>
          <div class='card-header bg-primary text-white'>
            <span class='logo'>DNS Packet Parser Tool</span>
          </div>
          <div class='card-body'>
            <div class='mb-3'>{{ info|safe }}</div>
            <form method='post' enctype='multipart/form-data'>
              <div class='mb-3'>
                <label for='file' class='form-label'>Select Excel or CSV file:</label>
                <input class='form-control' type='file' name='file' id='file' required>
              </div>
              <button type='submit' class='btn btn-primary'>Upload & Parse</button>
            </form>
            {% if msg %}
              <div class='mt-3 {% if "successfully" in msg %}msg-success{% else %}msg-error{% endif %}'>{{ msg }}</div>
            {% endif %}
            {% if download_url %}
              <div class='mt-4'>
                <a href='{{ download_url }}' class='btn btn-success'>Download Parsed File</a>
              </div>
            {% endif %}
          </div>
        </div>
        <div class='footer'>
          &copy; 2025 DNS Parser | Powered by Flask & Bootstrap
        </div>
      </div>
    </div>
  </div>
  <script src='https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js'></script>
</body>
</html>
"""

def parse_dns(packet_hex):
    try:
        packet_bytes = binascii.unhexlify(str(packet_hex))
        dns_record = dnslib.DNSRecord.parse(packet_bytes)
        return str(dns_record)
    except Exception as e:
        return f"Parse error: {e}"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    msg = ''
    download_url = None
    if request.method == 'POST':
        if 'file' not in request.files:
            msg = 'No file part'
        else:
            file = request.files['file']
            if file.filename == '':
                msg = 'No selected file'
            else:
                filename = secure_filename(file.filename)
                ext = os.path.splitext(filename)[1].lower()
                if ext not in ['.xlsx', '.xls', '.csv']:
                    msg = 'Unsupported file type.'
                else:
                    upload_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(upload_path)
                    try:
                        if ext == '.csv':
                            df = pd.read_csv(upload_path)
                        else:
                            df = pd.read_excel(upload_path)
                        if 'PacketData' not in df.columns:
                            msg = "No 'PacketData' column found in the file."
                        else:
                            df['DNSParsed'] = df['PacketData'].astype(str).apply(parse_dns)
                            parsed_filename = filename.rsplit('.', 1)[0] + '_parsed' + ext
                            parsed_path = os.path.join(PROCESSED_FOLDER, parsed_filename)
                            if ext == '.csv':
                                df.to_csv(parsed_path, index=False)
                            else:
                                df.to_excel(parsed_path, index=False)
                            download_url = url_for('download_file', filename=parsed_filename)
                            msg = 'File parsed successfully!'
                    except Exception as e:
                        msg = f'Error processing file: {e}'
    return render_template_string(HTML_TEMPLATE, info=INFO_TEXT, msg=msg, download_url=download_url)

@app.route('/download/<filename>')
def download_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    path = os.path.join(PROCESSED_FOLDER, filename)
    if os.path.exists(path):
        if ext == '.csv':
            return send_file(path, as_attachment=True, mimetype='text/csv')
        else:
            return send_file(path, as_attachment=True)
    else:
        flash('File not found.')
        return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True)
