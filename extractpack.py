from bs4 import BeautifulSoup
import csv

def extract_student_info(soup):
    
    info_table = soup.find('table', id="panel_FORM")

    student_info_table = info_table.find("table", class_="styleClass")

    # Find all <td> elements
    tds = student_info_table.find_all("td")
    
    # Initialize a dictionary to store extracted data
    student_info = {}

    # Mapping Persian labels to dictionary keys
    label_mapping = {
        "نام": "نام",
        "نام خانوادگي": "نام خانوادگی",
        "شماره دانشجويي": "شماره دانشجویی",
        "مقطع": "مقطع",
        "نيمسال ورود": "نیمسال ورود",
        "نيمسال پذيرش": "نیمسال پذیرش",
        "كل تعداد واحد اخذ شده": "كل تعداد واحد اخذ شده",
        "كل تعداد واحد گذرانده": "كل تعداد واحد گذرانده",
        "كد ملي": "کد ملی",
        "رشته": "رشته"
    }
    
    # Iterate over <td> elements in pairs (label and value)
    for i in range(0, len(tds) - 1, 2):
        label = tds[i].text.strip()
        value = tds[i + 1].text.strip()
        
        # Use label mapping to store data in the dictionary
        if label in label_mapping:
            student_info[label_mapping[label]] = value

    # Handle the case when <td> elements are not in pairs or missing data
    if len(tds) % 2 != 0:
        print("Warning: Odd number of <td> elements. Some data may be missing.")

    return student_info


# Extract terms info
def extract_term_dict(soup):
    term_dict = {}
    headterms = soup.find_all("caption", class_="caption")
    term_num = 1
    for headterm in headterms:
        head_text = headterm.text.strip()
        if head_text.startswith("نيمسال"):
            term_dict[term_num] = head_text.split("-")[-1].strip()
            term_num += 1
    return term_dict


# Function to find the number of tables based on panel__ IDs
def find_total_terms(soup):
    counter = 0
    while True:
        table_id = f"panel__{counter:02d}"
        # print(table_id)
        if not soup.find('table', id=table_id):  # Stop when no table is found
            break
        counter += 1
    return counter


# Function to write data to a CSV file
def write_to_csv(file_path, rows, append=True):
    """
    Writes rows to a CSV file. It supports both append and write modes.
    
    Args:
        file_path (str): Path to the CSV file.
        rows (list): A list of rows (each row is a list of column values).
        append (bool): Whether to append to the file (default: True).
    """
    mode = 'a' if append else 'w'
    with open(file_path, mode, newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(rows)

# Function to extract data from a specific table
def find_courses(soup, table_id, term_num, write_header=False, file_path=None):
    """
    Extracts course data from the HTML table and writes it to a CSV file.
    
    Args:
        soup (BeautifulSoup): Parsed HTML soup object.
        table_id (str): The ID of the table to extract.
        term_num (int): The term number to add as a prefix to the row.
        write_header (bool): Whether to write the header row to the CSV file.
        file_path (str): The path to the CSV file (optional).
    """
    term_dict = extract_term_dict(soup)
    term_name = term_dict.get(term_num, f"Term {term_num}")
    
    # Find the table by its ID
    term_table = soup.find('table', id=table_id)
    if term_table is None:
        print(f"Table with ID {table_id} not found.")
        return  # Exit if the table is not found

    # Extract all rows from the table
    rows = term_table.find_all("tr")
    
    # Prepare data for writing
    data_to_write = []
    
    for row_index, row in enumerate(rows):
        cols = row.find_all(['td', 'th'])  # Extract all table data or header cells
        row_data = [col.text.strip() for col in cols if col.text.strip()]  # Clean whitespace
        
        if not row_data:
            continue  # Skip empty rows

        if row_index == 0 and write_header:
            # If this is the header row and write_header is True, adjust the header
            adjusted_header = ["نیمسال"] + row_data
            data_to_write.append(adjusted_header)
        elif row_index > 0:
            # For normal rows, prepend the term name
            row_data[0] = term_name  # Replace first cell with the term name
            data_to_write.append(row_data)

    if file_path and data_to_write:
        # Write to CSV if file_path is provided
        write_to_csv(file_path, data_to_write, append=True)

# Function to find all term tables and extract data
def find_term_tables(soup, csv_file_path):
    """
    Finds tables with IDs like 'panel__00', 'panel__01', etc., extracts their data, 
    and writes it to a CSV file.
    
    Args:
        soup (BeautifulSoup): Parsed HTML soup object.
        file_path (str): Path to the CSV file for saving the data.
    """
    total_terms = find_total_terms(soup)  # Replace with actual function to get total terms
    print(f"Total terms: {total_terms}")
    
    for term_num in range(1, total_terms + 1):
        table_id = f"panel__{term_num - 1:02d}"  # Adjust the ID to match 'panel__00', 'panel__01', etc.
        write_header = (term_num == 1)  # Only write the header for the first term
        find_courses(soup, table_id, term_num, write_header=write_header, file_path=csv_file_path)
