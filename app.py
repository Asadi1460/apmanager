import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Cache the data loading function
@st.cache_data
def load_data():
    return pd.read_csv('courses.csv')

# Load data
df = load_data()
df['Total Units'] = df['Theoretical Units'] + df['Practical Units']


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
        width: 95%; /* Increased width */
        font-size: 13px; /* Smaller font size */
    }
    </style>
""", unsafe_allow_html=True)

# Apply the RTL and center class to the title
st.markdown('<h1 class="rtl center"> دانشگاه آزاد اسلامی واحد داراب</h1>', unsafe_allow_html=True)
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

# Define the new column names
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

# Rename the columns
df_to_show.rename(columns=new_column_names, inplace=True)

# Display selected courses
st.markdown('<h3 class="rtl center">دروس گذرانده</h3>', unsafe_allow_html=True)
st.markdown(f'<div class="rtl center">{df_to_show.to_html(classes="rtl-table", index=False)}</div>', unsafe_allow_html=True)

# Calculate total units
total_theoretical_units = selected_df['Theoretical Units'].sum()
total_practical_units = selected_df['Practical Units'].sum()
total_units = selected_df['Total Units'].sum()


# Define the required units for each course type
required_units_AD = {
    'پیش دانشگاهی': 4,
    'جبرانی': 0,
    'مقطع قبلی': 0,
    'عمومی': 18,
    'اختیاری': 0,
    'تربیتی': 14,
    'تخصصی': 43,
}

required_units_BD = {
    'پیش دانشگاهی': 0,
    'جبرانی': 8,
    'مقطع قبلی': 4,
    'عمومی': 10,
    'اختیاری': 10,
    'تربیتی': 9,
    'تخصصی': 43,
}

# Calculate remaining units
required_units = required_units_AD if stage == 'کاردانی' else required_units_BD

# Calculate units by course type
units_by_type = selected_df.groupby('Course Type')['Total Units'].sum().reindex(required_units.keys(), fill_value=0)

remaining_units = {course_type: required_units[course_type] - units_by_type[course_type]
                   for course_type in required_units.keys()}

# Create a DataFrame to display the results
results_df = pd.DataFrame({
    'نوع درس': required_units.keys(),
    'واحد گذرانده': units_by_type.values,
    'واحد الزامی': required_units.values(),
    'واحد مانده': remaining_units.values()
})

# Display the results table
st.markdown('<h3 class="rtl center">خلاصه وضعیت واحدها</h3>', unsafe_allow_html=True)
st.markdown(f'<div class="rtl center">{results_df.to_html(classes="rtl-table", index=False)}</div>', unsafe_allow_html=True)

# Calculate total remaining units
total_remain_units = sum(remaining_units.values())

# Display totals
st.markdown(f'<h3 class="rtl center" style="color: blue;">جمع کل واحدهای گذرانده: {total_units}</h3>', unsafe_allow_html=True)
st.markdown(f'<h3 class="rtl center" style="color: blue;">جمع کل واحدهای مانده: {total_remain_units}</h3>', unsafe_allow_html=True)

# Filter remaining courses
remaining_courses_df = filtered_df[~filtered_df['Course Name'].isin(selected_courses)]

# Rename the columns for the remaining courses
remaining_courses_df.rename(columns=new_column_names, inplace=True)

# Display remaining courses
st.markdown('<h3 class="rtl center">دروس باقیمانده</h3>', unsafe_allow_html=True)
st.markdown(f'<div class="rtl center">{remaining_courses_df.to_html(classes="rtl-table", index=False)}</div>', unsafe_allow_html=True)


# manager_email = 'pargaracademy@gmail.com'


# # Function to send email
# def send_email(subject, body, to):
#     msg = MIMEMultipart()
#     msg['From'] = manager_email
#     msg['To'] = to
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'html'))
#     try:
#         with smtplib.SMTP('smtp.gmail.com', 587) as server:
#             server.starttls()
#             server.login(manager_email, '')  # Use your App Password here
#             server.send_message(msg)
#         return True
#     except smtplib.SMTPAuthenticationError as e:
#         st.error(f"Authentication error: {e}")
#         return False
#     except Exception as e:
#         st.error(f"An error occurred: {e}")
#         return False

# # Your existing Streamlit app code here

# # Generate email content
# email_subject = "خلاصه وضعیت دانشجو"
# email_body = f"""
# <h3>خلاصه وضعیت واحدها</h3>
# {results_df.to_html(classes="rtl-table", index=False)}
# <h3>جمع کل واحدهای گذرانده: {total_units}</h3>
# <h3>جمع کل واحدهای مانده: {total_remain_units}</h3>
# <h3>دروس باقیمانده</h3>
# {remaining_courses_df.to_html(classes="rtl-table", index=False)}
# """

# # Email sending section
# st.markdown('<h3 class="rtl center">ارسال به مدیر گروه</h3>', unsafe_allow_html=True)
# email_to = st.text_input('آدرس ایمیل مدیر گروه', manager_email)
# if st.button('ارسال ایمیل'):
#     if send_email(email_subject, email_body, [email_to]):
#         st.success('ایمیل با موفقیت ارسال شد.')