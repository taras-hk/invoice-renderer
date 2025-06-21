import csv
from pathlib import Path
from typing import Dict, List

import pandas as pd


def read_companies_data(filepath: str) -> dict:
    """Read companies mapping from Excel file"""
    df = pd.read_excel(filepath, sheet_name="Sheet1")
    companies = {}
    for _, row in df.iterrows():
        company_id = row['company_id']
        companies[company_id] = {
            'name': row['company_name'],
            'address': row['company_address'],
            'registration_number': row['reg_number'],
            'vat_number': row['vat_number'],
            'bank_name': row['bank_name'],
            'iban': row['iban'],
            'swift': row['swift']
        }
    return companies

def process_invoice_data(invoice_data: dict, companies_map: dict) -> dict:
    """Replace company IDs with company details and generate invoice ID"""
    processed_data = invoice_data.copy()

    if 'invoice_date' in processed_data:
        if isinstance(processed_data['invoice_date'], pd.Timestamp):
            processed_data['invoice_date'] = processed_data['invoice_date'].strftime('%Y-%m-%d')
        else:
            processed_data['invoice_date'] = str(processed_data['invoice_date']).split()[0]

    if 'issued_by_id' in processed_data:
        company = companies_map.get(processed_data['issued_by_id'], {})
        processed_data['issued_by'] = company.get('name', '')
        processed_data['issued_by_address'] = company.get('address', '')
        processed_data['issued_by_registration_number'] = company.get('registration_number', '')
        processed_data['issued_by_vat_number'] = company.get('vat_number', '')
        processed_data['bank_name'] = company.get('bank_name', '')
        processed_data['iban'] = company.get('iban', '')
        processed_data['swift'] = company.get('swift', '')

    if 'issued_to_id' in processed_data:
        company = companies_map.get(processed_data['issued_to_id'], {})
        processed_data['issued_to'] = company.get('name', '')
        processed_data['issued_to_address'] = company.get('address', '')
        processed_data['issued_to_registration_number'] = company.get('registration_number', '')
        processed_data['issued_to_vat_number'] = company.get('vat_number', '')

    # Generate invoice ID only if we have all required data
    if processed_data.get('issued_by') and processed_data.get('issued_to') and 'invoice_date' in processed_data:
        processed_data['invoice_id'] = generate_invoice_id(
            processed_data['issued_by'],
            processed_data['issued_to'],
            processed_data['invoice_date']
        )

    return processed_data


def read_invoices_from_file(filepath: str) -> Dict[str, List[Dict]]:
    # Load company mappings
    companies_map = read_companies_data("companies_Data.xlsx")

    file_ext = Path(filepath).suffix.lower()
    result = {}

    if file_ext == '.csv':
        invoices = read_invoices_from_csv(filepath)
        result['default'] = [process_invoice_data(invoice, companies_map) for invoice in invoices]
    elif file_ext in ['.xlsx', '.xls']:
        sheet_data = read_invoices_from_excel(filepath)
        for sheet_name, invoices in sheet_data.items():
            result[sheet_name] = [process_invoice_data(invoice, companies_map) for invoice in invoices]
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")

    return result

def read_invoices_from_excel(filepath: str) -> Dict[str, List[Dict]]:
    """Read all sheets from Excel file"""
    try:
        all_sheets = pd.read_excel(filepath, sheet_name=None)
        result = {}

        for sheet_name, df in all_sheets.items():
            invoices = []
            for _, row in df.iterrows():
                invoice_data = row.to_dict()
                if all(field in invoice_data for field in ['issued_by_id', 'issued_to_id', 'invoice_date']):
                    # Convert numeric IDs to integers if they're floats
                    invoice_data['issued_by_id'] = int(invoice_data['issued_by_id'])
                    invoice_data['issued_to_id'] = int(invoice_data['issued_to_id'])
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
                # Convert string IDs to integers
                row['issued_by_id'] = int(row['issued_by_id'])
                row['issued_to_id'] = int(row['issued_to_id'])
                invoices_data.append(dict(row))

    except FileNotFoundError:
        print(f"Error: File {filepath} not found")
    except csv.Error as e:
        print(f"Error reading CSV file: {str(e)}")

    return invoices_data


def generate_invoice_id(issued_by: str, issued_to: str, date: str) -> str:
    # Remove spaces and get first 3 letters
    issued_by_prefix = issued_by.replace(" ", "")[:3].upper()
    issued_to_prefix = issued_to.replace(" ", "")[:3].upper()

    # Extract only the date part (before any space or time)
    date_only = str(date).split()[0]
    # Replace slashes with underscores in date
    formatted_date = date_only.replace("/", "").replace("-", "")

    # Combine all parts
    return f"{issued_by_prefix}{issued_to_prefix}{formatted_date}"
