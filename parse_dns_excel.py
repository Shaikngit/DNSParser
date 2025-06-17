import pandas as pd
import dnslib
import binascii
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def parse_dns(packet_hex):
    try:
        packet_bytes = binascii.unhexlify(packet_hex)
        dns_record = dnslib.DNSRecord.parse(packet_bytes)
        return str(dns_record)
    except Exception as e:
        return f"Parse error: {e}"

def main():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Excel or CSV file",
        filetypes=[("Excel/CSV files", "*.xlsx *.xls *.csv")]
    )
    if not file_path:
        messagebox.showinfo("No file selected", "Operation cancelled.")
        return

    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.csv':
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    if 'PacketData' not in df.columns:
        messagebox.showerror("Error", "No 'PacketData' column found in the file.")
        return

    df['DNSParsed'] = df['PacketData'].astype(str).apply(parse_dns)
    if ext == '.csv':
        output_path = file_path.rsplit('.', 1)[0] + "_parsed.csv"
        df.to_csv(output_path, index=False)
    else:
        output_path = file_path.rsplit('.', 1)[0] + "_parsed.xlsx"
        df.to_excel(output_path, index=False)
    messagebox.showinfo("Done", f"Parsed file saved as:\n{output_path}")

if __name__ == "__main__":
    main()
