import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
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
        for key, cell in the_table.get_celld().items():
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
        'جبرانی': 8,
        'مقطع قبلی': 4,
        'عمومی': 10,
        'اختیاری': 10,
        'تربیتی': 9,
        'تخصصی': 43,
    }
}

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
        font-size: 13px;
    }
    .dataframe-container {
        display: flex;
        justify-content: center;
    }
    .dataframe {
        text-align: center;
    }
    .dataframe th, .dataframe td {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Display titles
st.markdown('<h1 class="rtl center">دانشگاه آزاد اسلامی واحد داراب</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="rtl center">چک لیست انتخاب واحد</h2>', unsafe_allow_html=True)

# Stage Selection
stage = st.selectbox('انتخاب مقطع', df['Stage'].unique())

# Filter courses based on the selected stage
filtered_df = df[df['Stage'] == stage]

# Course Selection
selected_courses = st.multiselect('انتخاب دروس گذرانده', filtered_df['Course Name'])

# Filter selected courses
selected_df = filtered_df[filtered_df['Course Name'].isin(selected_courses)]
df_to_show = selected_df.copy()

# Define and rename columns
new_column_names = {
    'Stage': 'مقطع',
    'Course Name': 'نام درس',
    'Prerequisites': 'پیشنیاز',
    'Theoretical Units': 'واحد نظری',
    'Practical Units': 'واحد عملی',
    'Course Type': 'نوع درس',
    'description': 'توضیحات',
    'Total Units': 'جمع واحدها'
}

df_to_show.rename(columns=new_column_names, inplace=True)

# Display selected courses
st.markdown('<h3 class="rtl center">دروس گذرانده</h3>', unsafe_allow_html=True)

# Container for centering the table
st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
st.dataframe(df_to_show, hide_index=True, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Calculate total units
total_units = selected_df['Total Units'].sum()

# Calculate units by course type
units_by_type = selected_df.groupby('Course Type')['Total Units'].sum().reindex(required_units[stage].keys(), fill_value=0)
remaining_units = {course_type: required_units[stage][course_type] - units_by_type[course_type]
                   for course_type in required_units[stage].keys()}

# Create and display the results DataFrame
results_df = pd.DataFrame({
    'نوع درس': required_units[stage].keys(),
    'واحد گذرانده': units_by_type.values,
    'واحد الزامی': required_units[stage].values(),
    'واحد مانده': remaining_units.values()
})
st.markdown('<h3 class="rtl center">خلاصه وضعیت واحدها</h3>', unsafe_allow_html=True)
results_df = results_df[results_df.columns[::-1]]

st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
st.dataframe(results_df, hide_index=True, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Display totals
total_remain_units = sum(remaining_units.values())
st.markdown(f'<h3 class="rtl center" style="color: blue;">جمع کل واحدهای گذرانده: {total_units}</h3>', unsafe_allow_html=True)
st.markdown(f'<h3 class="rtl center" style="color: blue;">جمع کل واحدهای مانده: {total_remain_units}</h3>', unsafe_allow_html=True)

# Filter remaining courses and display
remaining_courses_df = filtered_df[~filtered_df['Course Name'].isin(selected_courses)]
remaining_courses_df.rename(columns=new_column_names, inplace=True)
remaining_courses_df = remaining_courses_df.sort_values(by='نوع درس')

st.markdown('<h3 class="rtl center">دروس باقیمانده</h3>', unsafe_allow_html=True)
st.dataframe(remaining_courses_df, hide_index=True, use_container_width=True)

# Button to download the PDF
if st.button('Generate PDF'):
    pdf_buffer = create_pdf(remaining_courses_df)
    st.download_button(
        label='Download PDF',
        data=pdf_buffer,
        file_name='dataframe.pdf',
        mime='application/pdf'
    )
