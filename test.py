import pandas as pd
import arabic_reshaper
from bidi.algorithm import get_display
from weasyprint import HTML

# Sample DataFrame
data = {
    'العمود1': [1, 2, 3, 4],
    'العمود2': [5, 6, 7, 8]
}
df = pd.DataFrame(data)

# Convert DataFrame to HTML with RTL support
def dataframe_to_html_rtl(df):
    html = df.to_html(index=False, justify='right')  # Right-align the text
    reshaped_html = arabic_reshaper.reshape(html)  # Reshape HTML
    display_html = get_display(reshaped_html)  # Display HTML correctly
    return display_html

# Generate HTML for DataFrame
html_content = dataframe_to_html_rtl(df)

# Create PDF from HTML
pdf = HTML(string=html_content).write_pdf()

# Save the PDF to a file
with open('output_rtl.pdf', 'wb') as f:
    f.write(pdf)