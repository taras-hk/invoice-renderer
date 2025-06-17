import csv
from pathlib import Path
from typing import Dict, List

import pandas as pd


def read_invoices_from_file(filepath: str) -> Dict[str, List[Dict]]:
    file_ext = Path(filepath).suffix.lower()

    if file_ext == '.csv':
        return {'default': read_invoices_from_csv(filepath)}
    elif file_ext in ['.xlsx', '.xls']:
        return read_invoices_from_excel(filepath)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")


def read_invoices_from_excel(filepath: str) -> Dict[str, List[Dict]]:
    """Read all sheets from Excel file"""
    try:
        all_sheets = pd.read_excel(filepath, sheet_name=None)
        result = {}

        for sheet_name, df in all_sheets.items():
            invoices = []
            for _, row in df.iterrows():
                # Convert row to dict and ensure all required fields exist
                invoice_data = row.to_dict()
                if all(field in invoice_data for field in ['issued_by', 'issued_to', 'invoice_date']):
                    invoice_id = generate_invoice_id(
                        str(invoice_data['issued_by']),
                        str(invoice_data['issued_to']),
                        str(invoice_data['invoice_date'])
                    )
                    invoice_data['invoice_id'] = invoice_id
                    invoices.append(invoice_data)
                else:
                    print(f"Warning: Missing required fields in row: {invoice_data}")
            result[sheet_name] = invoices

        return result
    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")
        return {}

def read_invoices_from_csv(filepath: str) -> List[Dict]:
    invoices_data = []

    try:
        with open(filepath, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                invoice_id = generate_invoice_id(row['issued_by'], row['issued_to'], row['invoice_date'])
                row['invoice_id'] = invoice_id
                invoices_data.append(dict(row))

    except FileNotFoundError:
        print(f"Error: File {filepath} not found")
    except csv.Error as e:
        print(f"Error reading CSV file: {str(e)}")

    return invoices_data


def generate_invoice_id(issued_by, issued_to, date):
    # Remove spaces and get first 3 letters
    issued_by_prefix = issued_by.replace(" ", "_")[:3].upper()
    issued_to_prefix = issued_to.replace(" ", "_")[:3].upper()

    # Extract only the date part (before any space or time)
    date_only = date.split()[0]
    # Replace slashes with underscores in date
    formatted_date = date_only.replace("/", "_")

    # Combine all parts
    invoice_id = f"{issued_by_prefix}_{issued_to_prefix}_{formatted_date}"
    return invoice_id
