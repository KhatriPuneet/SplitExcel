import streamlit as st
import os
import tempfile
from file_batch import process_file, get_unique_date_dir

st.title("Excel Batch Splitter")

st.write("Upload an Excel file to split it into smaller CSV chunks.")

uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

rows_per_file = st.number_input("Rows per file", min_value=100, value=5000, step=100)
prefix = st.text_input("Filename Prefix", value="B")

# Determine output path: Use local folder if available, else temp dir (for Cloud)
local_target_path = "/Users/Puneetkhatri/Documents/Daily Work"
if os.path.exists(local_target_path):
    base_output_path = local_target_path
else:
    # Fallback to a temporary directory for cloud deployment
    base_output_path = os.path.join(tempfile.gettempdir(), "excel_batch_output")
    if not os.path.exists(base_output_path):
        os.makedirs(base_output_path)

if uploaded_file is not None:
    if st.button("Process File"):
        with st.spinner("Processing..."):
            try:
                # Setup output directory
                output_dir, date_label = get_unique_date_dir(base_output_path)
                st.info(f"Saving files to: {output_dir}")

                # Pass the uploaded file object directly to pandas via our function
                generated_files = process_file(uploaded_file, output_dir, date_label, rows_per_file, prefix)
                
                st.success(f"Done! Created {len(generated_files)} files.")
                
                for filename in generated_files:
                    with open(filename, "rb") as f:
                        file_data = f.read()
                        st.download_button(
                            label=f"Download {filename}",
                            data=file_data,
                            file_name=filename,
                            mime="text/csv"
                        )
            except Exception as e:
                st.error(f"An error occurred: {e}")
