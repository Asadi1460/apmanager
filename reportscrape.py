from bs4 import BeautifulSoup
import requests
import re
import csv
import os
import pandas as pd
from fpdf import FPDF
from bidi.algorithm import get_display
import arabic_reshaper
import warnings
from extractpack import find_term_tables, extract_student_info

# Suppress UserWarnings
warnings.filterwarnings("ignore", category=UserWarning)


# Example usage
# Assuming `soup` is already a BeautifulSoup object of the parsed HTML

def main():
    # Clearing the Screen
    os.system('clear')

    main_path = "/Users/asadi/Downloads/Pdf test/"
    std_no = "078"
    # std_no = input("Std No: ")
    html_file_path = main_path + f"40116820627{std_no}.htm"
    
    csv_file_path = main_path + f"40116820627{std_no}.csv"
    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)
        print(f"File {csv_file_path} has been deleted.")
    # Load the HTML content
    with open(html_file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract and save data to CSV
    find_term_tables(soup, csv_file_path)
    student_info = extract_student_info(soup)
    
    # Output the extracted information
    print(student_info)


if __name__ == "__main__":
    main()



# def find_courses(table_id, term_num, write_header=False):
#     term_dict = extract_term_dict()
#     print(term_dict)

#     term_table = soup.find('table', id=table_id)
#     # Find all rows in the table
#     rows = term_table.find_all("tr")

#     with open(main_path + f"report{std_no}.csv", "a", newline='', encoding='utf-8') as file:
#         csv_writer = csv.writer(file)

#         for row_index, row in enumerate(rows):
#             cols = row.find_all(['td', 'th'])  # Only get table data or header cells
#             row_data = [col.text.strip() for col in cols if col.text.strip()]
            
#             # Check if this is the header row (usually the first row)
#             if row_index == 0 and write_header:
#                 # Adjust the header row by adding "ردیف" as the first element
                
#                 adjusted_header = ["نیمسال"] + row_data  # Shift other elements
#                 csv_writer.writerow(adjusted_header)
#                 continue  # Skip to the next row after writing the header
#             elif row_index == 0:
#                 continue
#             else:
#                 row_data[0] = term_dict[term_num]

            
#             # Write the row data (normal rows)
#             csv_writer.writerow(row_data)


# # Function to find tables with IDs like 'panel__00', 'panel__01', etc.
# def find_term_tables():
#     # Call the function to determine total_terms
#     total_terms = find_total_terms()
#     # Print the result
#     # print(f"Total terms: {total_terms}")
#     for i in range(total_terms):  # Adjust total_terms as needed
#         table_id = f"panel__{i:02d}"  # Dynamically create the table ID
#         if i == 0:
#             find_courses(table_id, term_num=i+1, write_header=True)
#         else:
#             find_courses(table_id, term_num=i+1)





######################################################################################################
# Load the CSV files
reports_df = pd.read_csv(main_path + f'report{std_no}.csv')

os.remove(f'{main_path}report{std_no}.csv')

courses_df = pd.read_csv('courses.csv')

print(courses_df.info())

courses_df = courses_df.drop(courses_df[courses_df['Course Name'].isin(['اصول بهداشت و کمک‌های اولیه ***', 'جامعه شناسی آموزش و پرورش ***'])].index)

related_major = input('1)مرتبط\n2)غیرمرتبط')
related_major = 'مرتبط' if related_major == '1' else 'غیرمرتبط'
if related_major == 'مرتبط':
    courses_df = courses_df[~(courses_df['Course Type'] == 'جبرانی')]

# print(courses_df[courses_df['Course Type'] == 'اختیاری'])

courses_df['Course Type'].unique()

# print(type(reports_df['نیمسال'][0]))

compensatory_passed_courses_codes = courses_df[courses_df['Course Type'] == 'تخصصی-جبرانی']['Code']

print(compensatory_passed_courses_codes)


courses_df.loc[courses_df['Course Type'] == 'اصلی-تربیتی', 'Course Type'] = 'اصلی'
courses_df.loc[courses_df['Course Type'] == 'پایه-تربیتی', 'Course Type'] = 'پایه'
courses_df.loc[courses_df['Course Type'] == 'تخصصی-جبرانی', 'Course Type'] = 'تخصصی'

courses_df['Course Type'].unique()


reports_df.drop(['كد ارائه', 'تعداد ساعت نظري', 'تعداد ساعت عملي', 
       'نوع درس',
    # 'نوع درس رشته',
    # 'وضعيت درس دانشجو', 
    'وضعيت درس در رشته',
       'وضعيت اخذ درس',
   #  'وضعيت حذف درس',
       'نمره با ضريب',
       'توضيحات'], axis=1, inplace=True)
# reports_df.columns


# Define the degree level (for now: کاردانی)
degree_level = "کارشناسی" if student_info['مقطع'].strip().startswith('كارشناس') else  "کاردانی"
# print(student_info)
# print(degree_level)


# 1. Filter for passed courses in the report
passed_courses_df = reports_df[reports_df['وضعيت قبولي'] == 'پاس شده']


# 2. Merge courses with the student's passed courses, filtering by degree level
# We assume the 'Stage' column in courses_df holds the degree level information

courses_df['Code'] = courses_df['Code'].astype('object')

# print(type(courses_df['Code']))

merged_df = pd.merge(courses_df[courses_df['Stage'] == degree_level], 
                     passed_courses_df, 
                     left_on='Code', 
                     right_on='كد درس', 
                     how='left')


# print(merged_df.columns)


merged_df.drop(['Stage', 'كد درس', 'نام درس', 'description', 'تعداد واحد نظري', 'تعداد واحد عملي', 'نوع درس رشته'], axis=1,inplace=True)

# print(merged_df['Course Type'] )

# print(merged_df)



# 3. Sum theoretical units per term
theoretical_units_per_term = passed_courses_df.groupby('نیمسال')['تعداد واحد نظري'].sum().reset_index()

# 4. Sum practical units by type per term (e.g., عملی-تخصصی, عملی-پایه)
practical_units_by_type_per_term = passed_courses_df.groupby(['نیمسال', 'نوع درس رشته'])['تعداد واحد عملي'].sum().reset_index()

# 5. Pivot the practical units to get them as columns by course type
practical_units_pivot = practical_units_by_type_per_term.pivot(index='نیمسال', columns='نوع درس رشته', values='تعداد واحد عملي').fillna(0)

# Rename columns to match the desired output format
practical_units_pivot = practical_units_pivot.rename(columns={
    'عمومي': 'واحد عملی عمومی',
    'پايه': 'واحد عملی پایه',
    'اصلي': 'واحد عملی اصلی',
    'تخصصي': 'واحد عملی تخصصی'
})

# Ensure missing columns are filled with zeros if they don't exist in the dataset
for col in ['واحد عملی عمومی',
            'واحد عملی پایه',
            'واحد عملی اصلی',
            'واحد عملی تخصصی',]:
    if col not in practical_units_pivot.columns:
        practical_units_pivot[col] = 0.0

# 6. Merge theoretical units with practical units by term
final_df = pd.merge(theoretical_units_per_term, practical_units_pivot, on='نیمسال', how='left')

# print(final_df.info())

final_df['جمع واحدها'] = final_df.iloc[:, 1:-1].sum(axis=1)
final_df['توضيحات'] = ' '
# print(final_df)

# Fill missing practical unit columns with 0
final_df = final_df.fillna(0)
# print(final_df.columns)
# 7. Sort the dataframe by term
final_df = final_df[['نیمسال',
                     'تعداد واحد نظري',
                     'واحد عملی عمومی',
                     'واحد عملی پایه',
                     'واحد عملی اصلی',
                     'واحد عملی تخصصی',
                     'جمع واحدها',
                     'توضيحات']]


# Optionally save the result to a CSV file
# final_df.to_csv(main_path + 'student_units_per_term.csv', index=False)

# Output the final DataFrame
# print(final_df)



final_df = final_df.loc[:,::-1]


# Initialize FPDF
pdf = FPDF(format='A4', orientation="landscape")

# Add a page
pdf.add_page()

# Add the Unicode font (after downloading the .ttf file)
pdf.add_font('Vazir', '', '/Users/asadi/Downloads/vazirmatn-v33.003/fonts/ttf/Vazirmatn-Regular.ttf', uni=True)

# Set the font for Persian text (UTF-8 characters)
pdf.set_font('Vazir', '', 12)

# Function to reshape and apply bidi for Persian text
def reshape_text(text):
    reshaped_text = arabic_reshaper.reshape(text)  # Reshape the text
    bidi_text = get_display(reshaped_text)  # Apply BiDi algorithm for proper display
    return bidi_text

# Add Title (Reshaped Persian text)
pdf.cell(200, 10, txt=reshape_text("دانشگاه آزاد اسلامی واحد داراب"), ln=True, align='C')
pdf.cell(200, 10, txt=reshape_text("گزارش وضعیت تحصیلی دانشجو"), ln=True, align='C')

# Add some space
pdf.ln(10)


count = 0
for key, value in student_info.items():
    # Add information in pairs, two per line
    pdf.cell(95, 10, txt=f"{reshape_text(value)}: {reshape_text(key)}", border=0, align='C')
    count += 1
    if count % 2 == 0:  # Move to a new line after every 2 items
        pdf.ln()

# If there are an odd number of items, ensure the last row gets a new line
if count % 2 != 0:
    pdf.ln()
# Add some space before the table
pdf.ln(10)

# Add table header
column_titles = ['نیمسال',
                 'تعداد واحد نظري',
                 'واحد عملی عمومی',
                 'واحد عملی پایه',
                 'واحد عملی اصلی',
                 'واحد عملی تخصصی',
                 'جمع واحدها',
                 'توضیحات']
column_titles = column_titles[::-1]
pdf.set_font('Vazir', '', 10)  # Bold font for header
for title in column_titles:
    pdf.cell(30, 10, txt=reshape_text(title), border=1, align='C')

pdf.ln()

# Iterate over the DataFrame rows
for index, row in final_df.iterrows():
    for item in row:
        # print(item)
        pdf.cell(30, 10, txt=str(item), border=1, align='C')
    pdf.ln()


cell_width = 210 / 3  # Divide the page width into three equal parts (about 70mm each)
pdf.cell(cell_width, 10, txt=reshape_text("مهر و امضاء مدیر آموزش"), border=0, align='C')
pdf.cell(cell_width, 10, txt=reshape_text("مهر و امضاء مدیر گروه"), border=0, align='C')
pdf.cell(cell_width, 10, txt=reshape_text("مهر و امضاء کارشناس گروه"), border=0, align='C')


# Save the PDF to a file
pdf.output(main_path + f"student_report{std_no}.pdf")

print("PDF generated successfully!")


passed_courses_df = merged_df[~merged_df['نمره'].isna()][['Code', 'Course Name', 'Course Type', 'Prerequisites', 'Theoretical Units', 'Practical Units']]
optional_passed_courses = passed_courses_df[passed_courses_df['Course Type'] == 'اختیاری']
optional_passed_courses_count = optional_passed_courses.shape[0]
print(optional_passed_courses, optional_passed_courses_count)

compensatory_passed_courses = passed_courses_df[passed_courses_df['Course Type'] == 'جبرانی']
compensatory_passed_courses_count = compensatory_passed_courses.shape[0]
print(compensatory_passed_courses, compensatory_passed_courses_count)
# print(passed_courses_df)


    
course_code = "90881"  # کد درس دفاع مقدس

# اطمینان از اینکه ستون 'Code' از نوع رشته است
passed_courses_df['Code'] = passed_courses_df['Code'].astype(str)

# بررسی اینکه آیا کد درس دفاع مقدس در ستون 'Code' وجود دارد
if passed_courses_df['Code'].str.contains(course_code).any():
    defence_course_passed = True
else:
    defence_course_passed = False    


# 3. Identify the remaining courses based on the degree level
remaining_courses_df = merged_df[merged_df['نمره'].isna()][['Code', 'Course Name', 'Course Type', 'Prerequisites', 'Theoretical Units', 'Practical Units']]

# print(remaining_courses_df['Course Name'])
if optional_passed_courses_count == 5 and defence_course_passed:
    remaining_courses_df = remaining_courses_df.drop(remaining_courses_df[remaining_courses_df['Course Type'].isin(['اختیاری'])].index)
# print(remaining_courses_df['Course Name'])

# if related_major == 'مرتبط':
#     remaining_courses_df = remaining_courses_df.drop(remaining_courses_df[remaining_courses_df['Code'].isin(compensatory_passed_courses_codes)].index)

if related_major == 'مرتبط':
    # اطمینان از اینکه ستون 'Code' و کدهای جبرانی از نوع رشته هستند
    remaining_courses_df['Code'] = remaining_courses_df['Code'].astype(str)
    compensatory_passed_courses_codes = compensatory_passed_courses_codes.astype(str)

    # حذف دروس جبرانی پاس شده از DataFrame
    remaining_courses_df = remaining_courses_df.drop(
        remaining_courses_df[remaining_courses_df['Code'].isin(compensatory_passed_courses_codes)].index
    )

# print(remaining_courses_df)


# Optionally, save the results to new CSV files
remaining_courses_df.to_csv(main_path + f'remaining_courses{std_no}.csv', index=False)