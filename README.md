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
python main.py --template <path_to_template> --data <path_to_csv> --output-dir <output_directory>
```

Example:
```bash
python main.py --template "C:\templates\invoice.html" --data "C:\data\invoices.csv" --output-dir "C:\output\invoices"
```