import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def main():
    parser = argparse.ArgumentParser(description="Generate PDF invoices from CSV data")
    parser.add_argument("--template", required=True, help="Path to HTML template file")
    parser.add_argument("--data", required=True, help="Path to CSV file with invoice data")
    parser.add_argument("--output-dir", required=True, help="Directory for output PDF files")

    args = parser.parse_args()

    # Validate input paths
    if not Path(args.template).exists():
        raise ValueError(f"Template file not found: {args.template}")
    if not Path(args.data).exists():
        raise ValueError(f"Data file not found: {args.data}")

    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    from data_reader import read_invoices_from_file
    sheets_data = read_invoices_from_file(args.data)

    for sheet_name, invoices in sheets_data.items():
        # Create sheet-specific directory for Excel files
        sheet_dir = output_dir
        if sheet_name != 'default':
            sheet_dir = output_dir / sheet_name
            sheet_dir.mkdir(exist_ok=True)

        for invoice_data in invoices:
            from renderer import create_invoice
            invoice_html = create_invoice(template_path=args.template, **invoice_data)

            pdf_file = sheet_dir / f"{invoice_data['invoice_id']}.pdf"
            render_pdf(invoice_html, str(pdf_file))


def render_pdf(html_input: str, output_pdf: str) -> bool:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            try:
                page.set_content(html_input, wait_until='networkidle')

                output_path = Path(output_pdf)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                page.pdf(path=output_pdf, format="A4")
                print(f"PDF successfully saved to {output_pdf}")
                return True

            except PlaywrightTimeout:
                print("Timeout while loading the page")
                return False
            except Exception as e:
                print(f"Error during PDF generation: {str(e)}")
                return False
            finally:
                browser.close()

    except Exception as e:
        print(f"Failed to initialize Playwright: {str(e)}")
        return False


def validate_input_path(path: str) -> bool:
    file_path = Path(path)
    return file_path.exists() and file_path.is_file() and file_path.suffix.lower() in ['.html', '.htm']


if __name__ == "__main__":
    main()
