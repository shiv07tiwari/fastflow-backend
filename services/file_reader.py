import io
import pdfplumber
import pandas as pd


def extract_text_from_pdf(pdf_bytes):
    text = ''
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + '\n'
    return text


def extract_data_from_csv(file_bytes):
    try:
        # Using StringIO to convert bytes to a string buffer
        csv_data = pd.read_csv(io.StringIO(file_bytes.decode()))
        return csv_data.to_csv(index=False)  # Convert DataFrame back to CSV format
    except pd.errors.ParserError as e:
        return {"error": "Failed to parse CSV file: " + str(e)}
