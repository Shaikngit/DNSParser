DNS Packet Parser Tool
=====================

This project provides a tool to parse DNS packet data from Excel or CSV files. It supports both a desktop (Tkinter) and a web (Flask) interface.

Features:
---------
- Upload Excel (.xlsx, .xls) or CSV files containing DNS packet data.
- Parses the 'PacketData' column using dnslib and adds a new column with the parsed DNS data.
- Download the processed file in the same format as uploaded.
- Modern web interface using Flask and Bootstrap.
- Desktop GUI for quick local use.

Setup Instructions:
-------------------
1. Install dependencies:
   pip install -r requirements.txt

2. To use the desktop tool:
   python parse_dns_excel.py

3. To use the web interface:
   python app.py
   Then open http://127.0.0.1:5000 in your browser.

Notes:
------
- The input file must contain a 'PacketData' column with DNS packet data in hex format.
- The .dnsparser folder is ignored by git and should not be committed.

Author: Your Name
Date: June 2025
