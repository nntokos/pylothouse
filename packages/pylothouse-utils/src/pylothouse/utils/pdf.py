import pandas as pd
from fpdf import FPDF

def csv_to_pdf(csv_file, cell_height=10, cell_width=None, pdf_file=None, border=True):
    """
    Convert a CSV file to a PDF file.
    :param csv_file: The CSV file to convert.
    :param cell_height: The height of each cell in the PDF.
    :param cell_width: The width of each cell in the PDF. If not provided, the width is calculated automatically based on the number of columns.
    :param pdf_file: The name of the PDF file to create. If not provided, the PDF file will have the same name as the CSV file with a .pdf extension.
    :param border: The border style for each cell. Default is 1.
    """
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Create a PDF object
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Calculate cell width if not provided
    if cell_width is None:
        cell_width = pdf.w / len(df.columns) - 2  # Subtracting 2 for padding

    # Add a cell for each column header
    for column in df.columns:
        pdf.cell(cell_width, cell_height, column, border, 0, 'C')
    pdf.ln()

    # Add a cell for each row
    for index, row in df.iterrows():
        for item in row:
            pdf.cell(cell_width, cell_height, str(item), border, 0, 'C')
        pdf.ln()

    # Save the PDF
    if pdf_file is None:
        pdf_file = csv_file.rsplit('.', 1)[0] + '.pdf'
    pdf.output(pdf_file)
