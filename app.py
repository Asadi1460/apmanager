import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
# from matplotlib.gridspec import GridSpec
import matplotlib.font_manager as fm
import arabic_reshaper
from bidi.algorithm import get_display
import io

# Load Persian font
font_path = 'Iranian Sans.ttf'  # Replace with the path to your Persian font file
persian_font = fm.FontProperties(fname=font_path)

# Function to reshape and bidi-process Persian text
def process_persian_text(text):
    if isinstance(text, str):
        reshaped_text = arabic_reshaper.reshape(text)
        return get_display(reshaped_text)
    return text

# Function to create a PDF from the DataFrame
def create_pdf(dataframe):
    # Apply the Persian text processing function to the entire DataFrame
    processed_df = dataframe.applymap(process_persian_text)
    processed_columns = [process_persian_text(col) for col in dataframe.columns]

    buffer = io.BytesIO()
    with PdfPages(buffer) as pdf:
        fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 size in inches
        
        ax.axis('tight')
        ax.axis('off')

        # Create table with processed DataFrame
        the_table = ax.table(cellText=processed_df.values, colLabels=processed_columns, cellLoc='right', loc='center')

        # Set font properties and style
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(12)
        the_table.auto_set_column_width(col=list(range(len(processed_columns))))

        # Style table cells
        for ـ, cell in the_table.get_celld().items():
            cell.set_text_props(fontproperties=persian_font)
            cell.set_edgecolor('black')
            cell.set_linewidth(1)

        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    buffer.seek(0)
    return buffer

# Cache the data loading function
@st.cache_data
def load_data():
    return pd.read_csv('courses.csv')

# Load and process data
df = load_data()
df['Total Units'] = df['Theoretical Units'] + df['Practical Units']

# Reverse column order from L2R to R2L
df = df[df.columns[::-1]]


# Use custom CSS for right-to-left direction and centering elements
st.markdown("""
    <style>
    .rtl {
        direction: rtl;
        text-align: right;
    }
    .center {
        text-align: center;
    }
    .rtl-table {
        direction: rtl;
        text-align: right;
        margin-left: auto;
        margin-right: auto;
        table-align: center;
        width: 95%;
        font-size: 14px;
    }
    .dataframe-container {
        display: flex;
        justify-content: center;
    }
    .dataframe, .dataframe th, .dataframe td {
        text-align: center;
    }
    .stTextInput, .stSelectbox, .stRadio, .stMultiSelect{
    direction: rtl;
    text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

# Display titles
st.markdown('<h1 class="rtl center">دانشگاه آزاد اسلامی واحد داراب</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="rtl center">چک لیست انتخاب واحد</h2>', unsafe_allow_html=True)

# Input text box for student number
student_number = st.text_input("شماره دانشجویی:")

# Stage Selection
stage = st.selectbox('انتخاب مقطع', df['Stage'].unique())


# Creating radio buttons
related_major = 'مرتبط'
if stage == 'کارشناسی':
    related_major = st.radio('نوع مدرک کاردانی را انتخاب کنید:', ['مرتبط', 'غیرمرتبط'], index=1, horizontal=True)


# Define the required units for each course type
required_units = {
    'کاردانی': {
        'پیش دانشگاهی': 4,
        'جبرانی': 0,
        'مقطع قبلی': 0,
        'عمومی': 18,
        'اختیاری': 0,
        'تربیتی': 14,
        'تخصصی': 43,
    },
    'کارشناسی': {
        'پیش دانشگاهی': 0,
        'جبرانی': 8 if related_major == 'غیرمرتبط' else 0,
        'مقطع قبلی': 4,
        'عمومی': 10,
        'اختیاری': 10,
        'تربیتی': 9,
        'تخصصی': 43,
    }
}

# Filter courses based on the selected stage
filtered_df = df[df['Stage'] == stage]

if related_major == 'مرتبط':
    filtered_df = filtered_df[~(filtered_df['Course Type'] == 'جبرانی')]

# Course Selection
selected_courses = st.multiselect('انتخاب دروس گذرانده', filtered_df['Course Name'])

# Filter selected courses
selected_df = filtered_df[filtered_df['Course Name'].isin(selected_courses)]

# Create a copy of the selected DataFrame
df_to_show = selected_df.copy()

# Define and rename columns
new_column_names = {
    'Stage': 'مقطع',
    'Code': 'کد درس',
    'Course Name': 'نام درس',
    'Prerequisites': 'پیشنیاز',
    'Theoretical Units': 'واحد نظری',
    'Practical Units': 'واحد عملی',
    'Course Type': 'نوع درس',
    'description': 'توضیحات',
    'Total Units': 'جمع واحدها'
}

# # Display selected courses ######################
# df_to_show.rename(columns=new_column_names, inplace=True)

# st.markdown('<h3 class="rtl center">دروس گذرانده</h3>', unsafe_allow_html=True)

# # Select all columns starting from the second column onward
# df_to_show = df_to_show.iloc[:, :-1]

# # Container for centering the table
# st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
# st.dataframe(df_to_show, hide_index=True, use_container_width=True)
# st.markdown('</div>', unsafe_allow_html=True)

# Calculate total units
total_units = selected_df['Total Units'].sum()

# Calculate units by course type
units_by_type = selected_df.groupby('Course Type')['Total Units'].sum().reindex(required_units[stage].keys(), fill_value=0)
remaining_units = {course_type: required_units[stage][course_type] - units_by_type[course_type]
                   for course_type in required_units[stage].keys()}

total_remain_units = sum(remaining_units.values())
total_required_units = sum(required_units[stage].values())

# Display totals
st.markdown(f'<h3 class="rtl center" style="color: blue;">جمع کل واحدهای گذرانده: {total_units}</h3>', unsafe_allow_html=True)
st.markdown(f'<h3 class="rtl center" style="color: red;">جمع کل واحدهای مانده: {total_remain_units}</h3>', unsafe_allow_html=True)


# Create and display the results DataFrame
results_df = pd.DataFrame({
    'نوع درس': required_units[stage].keys(),
    'واحد گذرانده': units_by_type.values,
    'واحد الزامی': required_units[stage].values(),
    'واحد مانده': remaining_units.values()
})



results_df.loc[len(results_df)] = ['جــــــــمــــــــع کــــــــــــل', 
                                   total_units, 
                                   total_required_units, 
                                   total_remain_units]

st.markdown('<h3 class="rtl center">خلاصه وضعیت واحدها</h3>', unsafe_allow_html=True)
results_df = results_df[results_df.columns[::-1]]

st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
st.dataframe(results_df, hide_index=True, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Filter remaining courses and display
remaining_courses_df = filtered_df[~filtered_df['Course Name'].isin(selected_courses)].copy()
remaining_courses_df.rename(columns=new_column_names, inplace=True)
# remaining_courses_df = remaining_courses_df.drop(['مقطع'], axis=1)
# Select all columns starting from the second column onward
remaining_courses_df = remaining_courses_df.iloc[:, :-1]

sort_dict = {
    'نوع درس': True, 
    'واحد عملی' : False,
    'پیشنیاز': False,
}

remaining_courses_df = remaining_courses_df.sort_values(by=list(sort_dict.keys()), ascending=list(sort_dict.values()))


st.markdown('<h3 class="rtl center">دروس باقیمانده</h3>', unsafe_allow_html=True)
st.dataframe(remaining_courses_df, hide_index=True, use_container_width=True)


# Button to download the PDF
if st.button('Generate PDF'):
    pdf_buffer = create_pdf(remaining_courses_df)
    
    st.download_button(
        label='Download PDF',
        data=pdf_buffer,
        file_name = student_number + '.pdf' if student_number else 'output.pdf',
        mime='application/pdf'
    )

st.markdown('<h6 class="rtl center">برنامه‌نویس:  دکتر محمد علی اسدی</h6>', unsafe_allow_html=True)
telegram_id = '@drasadi277'
phone_no = '09393338100'
st.markdown(f'<h6 class="rtl center">تلفن: {phone_no}</h6>', unsafe_allow_html=True)
st.markdown(f'<h6 class="center">ID: {telegram_id}</h6>', unsafe_allow_html=True)


