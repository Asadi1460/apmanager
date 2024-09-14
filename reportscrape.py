from bs4 import BeautifulSoup
import requests
import re
import csv
import os

# os.
file_path = "/Users/asadi/Downloads/Pdf test/0531/40116820627032.htm"


# Load the HTML content
with open(file_path, "r", encoding="utf-8") as file:
    content = file.read()

# Parse the HTML content
soup = BeautifulSoup(content, 'html.parser')

# Initialize variables to store total units and other details
total_units_passed = 0
semester_data = []


# Function to find the number of tables based on panel__ IDs
def find_max_tables(soup):
    i = 0
    while True:
        table_id = f"panel__{i:02d}"
        # print(table_id)
        if not soup.find('table', id=table_id):  # Stop when no table is found
            break
        i += 1
    return i

# Call the function to determine max_tables
max_tables = find_max_tables(soup)

# Print the result
print(f"Total terms found: {max_tables}")


# def find_courses(table_id):
#     term_table = soup.find('table', id=table_id)

#     rows = term_table.find_all("tr")

#     with open("tmp.csv", "a") as file:
#         csv_writer = csv.writer(file)
        
#         for item in range(len(rows)):
#             csv_writer.writerow([t.text.strip() for t in rows[item]])


# def find_courses(table_id):
#     term_table = soup.find('table', id=table_id)

#     # Find all rows in the table
#     rows = term_table.find_all("tr")

#     with open("tmp.csv", "a", newline='') as file:  # Ensure 'newline' to avoid extra lines in CSV
#         csv_writer = csv.writer(file)
        
#         for row in rows:
#             # Extract all <td> or <th> elements from the row
#             cols = row.find_all(['td', 'th'])  # This filters out only table data or headers
#             csv_writer.writerow([col.text.strip() for col in cols if col.text.strip()])  # Avoid blank columns

# def find_courses(table_id, first_table=False):
#     term_table = soup.find('table', id=table_id)

#     # Find all rows in the table
#     rows = term_table.find_all("tr")

#     # Open the CSV file in append mode
#     with open("tmp.csv", "a", newline='') as file:
#         csv_writer = csv.writer(file)
        
#         # Determine if we need to skip the first header row
#         header_skipped = not first_table  # If it's the first table, don't skip header
        
#         for row in rows:
#             cols = row.find_all(['td', 'th'])  # Only get table data or header cells
#             row_data = [col.text.strip() for col in cols if col.text.strip()]

#             # Skip the first header row if not the first table
#             if header_skipped:
#                 header_skipped = False  # Skip only the first header
#                 continue  # Skip the first row (header) after this

#             # Write the row data to CSV
#             csv_writer.writerow(row_data)


def find_courses(table_id, write_header=False):
    term_table = soup.find('table', id=table_id)

    # Find all rows in the table
    rows = term_table.find_all("tr")

    with open("tmp.csv", "a", newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)

        for row_index, row in enumerate(rows):
            cols = row.find_all(['td', 'th'])  # Only get table data or header cells
            row_data = [col.text.strip() for col in cols if col.text.strip()]
            
            # Check if this is the header row (usually the first row)
            if row_index == 0 and write_header:
                # Adjust the header row by adding "ردیف" as the first element
                adjusted_header = ['ردیف'] + row_data  # Shift other elements
                csv_writer.writerow(adjusted_header)
                continue  # Skip to the next row after writing the header
            elif row_index == 0:
                continue
            
            # Write the row data (normal rows)
            csv_writer.writerow(row_data)


# Function to find tables with IDs like 'panel__00', 'panel__01', etc.
def find_term_tables(max_tables):
    tables = []
    for i in range(max_tables):  # Adjust max_tables as needed
        table_id = f"panel__{i:02d}"  # Dynamically create the table ID
        if i == 0:
            find_courses(table_id, write_header=True)
        else:
            find_courses(table_id)

    #     if term_table:
    #         tables.append(term_table)
    #     else:
    #         print(f"Table with ID {table_id} not found.")
    
    # return tables

# Call the function to find tables
tables = find_term_tables(max_tables)

# # Print the content of each found table
# for i, table in enumerate(tables, start=1):
#     print(f"--- Table {i} ---")
#     print(table.prettify())  # Print a formatted version of the table




    

