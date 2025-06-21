# Invoice Renderer

A simple Python application that generates PDF invoices from CSV data using HTML templates.

## Prerequisites

- Python 3.8+
- pip

## Installation

```bash
pip install -r requirements.txt
```

## Usage
Run the application with the following command:
```bash
python main.py --template <path_to_template> --data <path_to_xlsx> --companies <path_to_companies_data> --output-dir <output_directory>
```

Example:

```bash
python main.py --template "C:\templates\invoice.html" --data "C:\data\invoices.xlsx" --output-dir "C:\output\invoices" --companies "C:\data\companies.xlsx"
```

### Input File Requirements

#### Excel Files (`.xlsx`, `.xls`)
- Each sheet will be processed separately
- Required columns:
  - `issued_by_id` (integer)
  - `issued_to_id` (integer)
  - `invoice_date` (date format)
- Additional columns will be preserved in output

#### CSV Files (`.csv`)
- Must contain the same required columns as Excel
- UTF-8 encoding
- Standard CSV format

### Companies Data File

File name: `companies_Data.xlsx`
Required structure:
```
Sheet1:
- company_id (integer)
- company_name (text)
- company_address (text)
- reg_number (text)
- vat_number (text)
- bank_name (text)
- iban (text)
- swift (text)
```

`Sheet1` is the default sheet name where companies data is stored.

### Data Processing
1. The app reads company details from `companies_Data.xlsx`
2. For each invoice in the input file:
   - Maps company IDs to full company details
   - Formats dates to `YYYY-MM-DD`
   - Generates unique invoice ID using format: `{ISSUER_PREFIX}{RECIPIENT_PREFIX}{YYYYMMDD}`
   - Adds bank details from the issuing company

### Common Errors to Avoid
- Missing required columns in input files
- Non-integer company IDs
- Missing company entries in companies data file
- Incorrect date formats
- Wrong file encodings for CSV

The processed data can then be used for invoice generation or further processing.