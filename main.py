import tkinter as tk
from tkinter import filedialog, messagebox
import random
from datetime import datetime
import os
import shutil
from fpdf import FPDF
import sqlite3


class PositivePayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Positive Pay Tool")

        # Generate Data Button
        self.generate_data_button = tk.Button(self.root, text="Generate Positive Pay File", command=self.generate_data)
        self.generate_data_button.pack(pady=10)

        # Text Widget to display data
        self.text_widget = tk.Text(self.root, height=15, width=50)
        self.text_widget.pack(pady=10)

        # Export Button
        self.export_button = tk.Button(self.root, text="Export Positive Pay Data", command=self.export_data)
        self.export_button.pack(pady=10)

        # Nightly Report Button
        self.nightly_report_button = tk.Button(self.root, text="Generate Nightly Report",
                                               command=self.generate_nightly_report)
        self.nightly_report_button.pack(pady=10)

        # Database connection
        self.conn = sqlite3.connect('transactions.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def generate_data(self):
        """Generate a Positive Pay file with random data."""
        filename = "temp_positive_pay_file.txt"
        with open(filename, 'w') as file:
            for _ in range(10):
                check_number = random.randint(1000, 9999)
                payee = "Company " + str(random.randint(1, 10))
                amount = round(random.uniform(100.0, 1000.0), 2)
                issue_date = datetime.now().strftime('%Y-%m-%d')
                file.write(f"{check_number}\t{payee}\t{amount}\t{issue_date}\n")

        self.display_data(filename)
        messagebox.showinfo("Data Generated", "Positive Pay file has been generated.")

    def display_data(self, filename):
        """Display the data in the text widget."""
        with open(filename, 'r') as file:
            lines = file.readlines()
            self.text_widget.delete("1.0", tk.END)
            for line in lines:
                self.text_widget.insert(tk.END, line)

    def export_data(self):
        """Export the data to specified paths."""
        upload_path = "C:/Users/kenne/PycharmProjectt/The Positive Pay Solution/UPLOAD"
        backup_path = "C:/Users/kenne/PycharmProjectt/The Positive Pay Solution/BACKUP"

        # Ensure directories exist
        os.makedirs(upload_path, exist_ok=True)
        os.makedirs(backup_path, exist_ok=True)

        # Define the filename format
        current_time = datetime.now().strftime('%m%d%y%H%M%S')
        export_filename = f"pospay_fileexport_{current_time}.txt"

        # Move the file to the desired locations
        shutil.copy("temp_positive_pay_file.txt", os.path.join(upload_path, export_filename))
        shutil.copy("temp_positive_pay_file.txt", os.path.join(backup_path, export_filename))

        # Remove the original file
        os.remove("temp_positive_pay_file.txt")

        # Save data to database
        data = []
        with open(os.path.join(upload_path, export_filename), 'r') as file:
            lines = file.readlines()
            for line in lines[1:]:
                check_number, payee, amount, issue_date = line.strip().split('\t')
                data.append((int(check_number), payee, float(amount), issue_date))
        self.save_to_db(data)

        messagebox.showinfo("Data Exported", f"Positive Pay file has been exported as {export_filename}.")

    def create_table(self):
        """Create a table if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                CheckNumber INTEGER,
                Payee TEXT,
                Amount REAL,
                IssueDate TEXT
            )
        """)
        self.conn.commit()

    def save_to_db(self, data):
        """Save transactions to the database."""
        self.cursor.executemany("INSERT INTO transactions VALUES (?, ?, ?, ?)", data)
        self.conn.commit()

    def fetch_all_data(self):
        """Fetch all transactions from the database."""
        self.cursor.execute("SELECT * FROM transactions")
        return self.cursor.fetchall()

    def generate_nightly_report(self):
        try:
            print("Generating nightly report...")

            # Fetch data from the database for the nightly report
            all_records = self.fetch_all_data()
            print(f"Number of records: {len(all_records)}")

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Nightly Report", ln=True, align='C')
            pdf.ln(10)

            # Column headers
            pdf.cell(40, 10, "CheckNumber", border=1)
            pdf.cell(40, 10, "Payee", border=1)
            pdf.cell(40, 10, "Amount", border=1)
            pdf.cell(40, 10, "IssueDate", border=1)
            pdf.ln()

            # Data
            total_amount = 0
            for record in all_records:
                check_number, payee, amount, issue_date = record
                pdf.cell(40, 10, str(check_number), border=1)
                pdf.cell(40, 10, payee, border=1)
                pdf.cell(40, 10, f"${amount:.2f}", border=1)
                pdf.cell(40, 10, issue_date, border=1)
                pdf.ln()
                total_amount += amount

            pdf.cell(120, 10, "Total Amount:", border=1)
            pdf.cell(40, 10, f"${total_amount:.2f}", border=1)
            pdf.ln()

            # Save to Report/Nightly directory with a timestamped name
            report_dir = "Report/Nightly"
            os.makedirs(report_dir, exist_ok=True)
            current_time = datetime.now().strftime('%m%d%y')
            report_filename = os.path.join(report_dir, f"pospay_nightlyreport_{current_time}.pdf")
            pdf.output(report_filename)
            os.startfile(report_filename)

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PositivePayApp(root)
    root.mainloop()
