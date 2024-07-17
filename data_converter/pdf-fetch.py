import pdfplumber
import pandas as pd
import re
from typing import List, Dict, Optional, Union

# Path to the PDF file
pdf_path = 'C:/Users/HP/Downloads/DXBinteract market report (1).pdf'

data = []

with pdfplumber.open(pdf_path) as pdf:
    pages = pdf.pages  # Get the pages of the PDF
    for page_number, page in enumerate(pages):  # Iterate through each page by index
        # Extract tables from the page
        tables = page.extract_tables()
        for table_number, table in enumerate(tables):  # Iterate through each table by index
            # Specifically handle the first page
            if page_number == 0:
                # Attempt to identify the table by finding a row that matches the expected headers
                start_index = next(
                    (i for i, row in enumerate(table) if row and any('Location' in str(cell) for cell in row)), None)
                if start_index is not None:
                    # Adjust here: Ensure the row is properly formatted before extending data
                    for row in table[start_index + 1:]:  # Start from the first row of actual data
                        # Clean each row: remove None and strip strings to ensure no leading/trailing whitespace or commas
                        cleaned_row = [cell.strip() if isinstance(cell, str) else '' for cell in row]
                        data.append(cleaned_row)
            # Skip the header row
            else:
                data.extend(table)

# Ensure we have data to process
if not data:
    print("No data extracted, please check the PDF structure.")
else:
    # Create a DataFrame using the first line as the header
    df = pd.DataFrame(data[1:], columns=data[0])  # Assuming the first row of data has headers

    # Save to CSV
    csv_path = '../property_sales_history_downtown_dubai.csv'
    df.to_csv(csv_path, index=False)

    print("Data has been extracted and saved to CSV file.")

with open(csv_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Prepare a list to collect data dictionaries, with type hints
data: List[Dict[str, Optional[str]]] = []

# Regex to correctly extract the required information
regex = r"([^,]+, [^0-9]+) (\d{1,2}/\d{1,2}/\d{4}) (\d+,\d+).*?(\d+ Beds)"

for line in lines:
    if line.strip():  # Check that the line is not empty
        match = re.match(regex, line.replace('\n', ''))
        if match:
            location = match.group(1)
            date = match.group(2)
            sold_for = match.group(3).replace(',', '')  # Remove commas for clarity
            specs = match.group(4)

            # Append to the data list, with None checks as optional
            data.append({
                "Location": location.strip(),
                "Date": date.strip(),
                "Sold for": sold_for.strip(),
                "Specs": specs.strip()
            })

# Create a DataFrame with the data
df = pd.DataFrame(data)

# Path to create the Excel file
excel_path = '../structured_property_sales_history_downtown_dubai.xlsx'

# Write to an Excel file
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Sales History')

print("The data has been structured and saved in an Excel file.")
