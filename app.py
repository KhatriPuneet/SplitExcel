import streamlit as st
import os
import tempfile
from datetime import datetime
from file_batch import process_file, get_unique_date_dir, merge_files

# Sidebar for App Selection
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Choose an App", ["Split Excel", "Merge Excel"])

if app_mode == "Split Excel":
    st.title("Excel Batch Splitter v1.0.0")

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
        if "generated_files" not in st.session_state:
            st.session_state.generated_files = []

        if st.button("Process File"):
            with st.spinner("Processing..."):
                try:
                    # Setup output directory
                    output_dir, date_label = get_unique_date_dir(base_output_path)
                    st.info(f"Saving files to: {output_dir}")

                    # Pass the uploaded file object directly to pandas via our function
                    generated_files = process_file(uploaded_file, output_dir, date_label, rows_per_file, prefix)
                    
                    # Store in session state
                    st.session_state.generated_files = generated_files
                    st.success(f"Done! Created {len(generated_files)} files.")
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")

        # Display results if files exist in session state
        if st.session_state.generated_files:
            generated_files = st.session_state.generated_files
            
            import base64
            import streamlit.components.v1 as components
            import json

            # Prepare file data as JSON
            files_data = []
            for file_path in generated_files:
                with open(file_path, "rb") as f:
                    data = f.read()
                    b64 = base64.b64encode(data).decode()
                    filename = os.path.basename(file_path)
                    files_data.append({"filename": filename, "b64": b64, "mime": "text/csv"})
            
            files_json = json.dumps(files_data)

            # Custom HTML/JS Component
            # 1. Styles the button (Blue/White)
            # 2. Uses File System Access API (showDirectoryPicker) to save all files to a selected folder
            # 3. Fallback to individual downloads if API not supported
            components.html(f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                .download-btn {{
                    background-color: #007bff; /* Blue */
                    border: none;
                    color: white; /* White Text */
                    padding: 12px 24px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;
                    cursor: pointer;
                    border-radius: 8px; /* Rounded Corners */
                    font-family: sans-serif;
                    transition: background-color 0.3s;
                }}
                .download-btn:hover {{
                    background-color: #0056b3;
                }}
                .status {{
                    margin-top: 10px;
                    font-family: sans-serif;
                    color: #333;
                    font-size: 14px;
                }}
            </style>
            </head>
            <body>
                <button id="dl-btn" class="download-btn" onclick="downloadFiles()">Download Files</button>
                <div id="status" class="status"></div>

                <script>
                    const files = {files_json};
                    const statusDiv = document.getElementById('status');
                    const btn = document.getElementById('dl-btn');

                    async function downloadFiles() {{
                        btn.disabled = true;
                        btn.innerText = "Saving...";
                        
                        // Try to use File System Access API (Modern Browsers)
                        if (window.showDirectoryPicker) {{
                            try {{
                                const dirHandle = await window.showDirectoryPicker();
                                statusDiv.innerText = "Saving files to selected folder...";
                                
                                for (const file of files) {{
                                    const fileHandle = await dirHandle.getFileHandle(file.filename, {{ create: true }});
                                    const writable = await fileHandle.createWritable();
                                    
                                    // Convert Base64 to Blob
                                    const byteCharacters = atob(file.b64);
                                    const byteNumbers = new Array(byteCharacters.length);
                                    for (let i = 0; i < byteCharacters.length; i++) {{
                                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                                    }}
                                    const byteArray = new Uint8Array(byteNumbers);
                                    const blob = new Blob([byteArray], {{type: file.mime}});
                                    
                                    await writable.write(blob);
                                    await writable.close();
                                }}
                                statusDiv.innerText = "✅ All files saved successfully!";
                                statusDiv.style.color = "green";
                            }} catch (err) {{
                                console.error(err);
                                statusDiv.innerText = "❌ Error or cancelled: " + err.message;
                                statusDiv.style.color = "red";
                                // Fallback?
                            }}
                        }} else {{
                            // Fallback for browsers without File System Access API
                            statusDiv.innerText = "⚠️ Browser doesn't support folder selection. Downloading individually...";
                            files.forEach((file, index) => {{
                                setTimeout(() => {{
                                    var a = document.createElement('a');
                                    a.href = 'data:' + file.mime + ';base64,' + file.b64;
                                    a.download = file.filename;
                                    a.style.display = 'none';
                                    document.body.appendChild(a);
                                    a.click();
                                    document.body.removeChild(a);
                                }}, index * 800);
                            }});
                        }}
                        
                        btn.disabled = false;
                        btn.innerText = "Download Files";
                    }}
                </script>
            </body>
            </html>
            """, height=150)

            st.divider()
            st.write("### Individual Files")
            for filename in generated_files:
                with open(filename, "rb") as f:
                    file_data = f.read()
                    st.download_button(
                        label=f"Download {os.path.basename(filename)}",
                        data=file_data,
                        file_name=os.path.basename(filename),
                        mime="text/csv",
                        key=filename # Unique key for each button
                    )

elif app_mode == "Merge Excel":
    st.title("Excel Batch Merger")
    st.write("Upload multiple Excel or CSV files to merge them into one file.")
    
    uploaded_files = st.file_uploader("Choose Excel/CSV files", type=["xlsx", "xls", "csv"], accept_multiple_files=True)
    
    if uploaded_files:
        # Initialize session state for merge results
        if "merged_file_path" not in st.session_state:
            st.session_state.merged_file_path = None
        if "merged_filename" not in st.session_state:
            st.session_state.merged_filename = None

        if st.button("Merge Files"):
            with st.spinner("Merging..."):
                try:
                    # Determine output path: Prioritize Downloads, then local work path, then temp
                    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
                    local_target_path = "/Users/Puneetkhatri/Documents/Daily Work"
                    
                    if os.path.exists(downloads_path):
                        base_merge_path = downloads_path
                    elif os.path.exists(local_target_path):
                        base_merge_path = local_target_path
                    else:
                        base_merge_path = os.path.join(tempfile.gettempdir(), "excel_merge_output")
                    
                    if not os.path.exists(base_merge_path):
                        os.makedirs(base_merge_path)

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_filename = f"merged_output_{timestamp}.xlsx"
                    output_path = os.path.join(base_merge_path, output_filename)
                    
                    # Merge
                    result_path = merge_files(uploaded_files, output_path)
                    
                    if result_path:
                        st.session_state.merged_file_path = result_path
                        st.session_state.merged_filename = output_filename
                    else:
                        st.warning("No data found to merge.")
                        
                except Exception as e:
                    st.error(f"An error occurred during merge: {e}")

        # Display results if merge was successful
        if st.session_state.merged_file_path and os.path.exists(st.session_state.merged_file_path):
            result_path = st.session_state.merged_file_path
            output_filename = st.session_state.merged_filename
            
            st.success(f"Files merged successfully! Saved to: {result_path}")
            
            import base64
            import json
            import streamlit.components.v1 as components

            # Prepare file data for JavaScript
            with open(result_path, "rb") as f:
                file_data = f.read()
                b64 = base64.b64encode(file_data).decode()
            
            files_data = [{"filename": output_filename, "b64": b64, "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}]
            files_json = json.dumps(files_data)

            # Custom HTML/JS Component for folder selection
            components.html(f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                .download-btn {{
                    background-color: #28a745; /* Green */
                    border: none;
                    color: white;
                    padding: 12px 24px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;
                    cursor: pointer;
                    border-radius: 8px;
                    font-family: sans-serif;
                    transition: background-color 0.3s;
                }}
                .download-btn:hover {{
                    background-color: #218838;
                }}
                .status {{
                    margin-top: 10px;
                    font-family: sans-serif;
                    color: #333;
                    font-size: 14px;
                }}
            </style>
            </head>
            <body>
                <button id="dl-btn" class="download-btn" onclick="downloadFiles()">Save to Folder</button>
                <div id="status" class="status"></div>

                <script>
                    const files = {files_json};
                    const statusDiv = document.getElementById('status');
                    const btn = document.getElementById('dl-btn');

                    async function downloadFiles() {{
                        btn.disabled = true;
                        btn.innerText = "Saving...";
                        
                        if (window.showDirectoryPicker) {{
                            try {{
                                const dirHandle = await window.showDirectoryPicker();
                                statusDiv.innerText = "Saving file to selected folder...";
                                
                                for (const file of files) {{
                                    const fileHandle = await dirHandle.getFileHandle(file.filename, {{ create: true }});
                                    const writable = await fileHandle.createWritable();
                                    
                                    const byteCharacters = atob(file.b64);
                                    const byteNumbers = new Array(byteCharacters.length);
                                    for (let i = 0; i < byteCharacters.length; i++) {{
                                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                                    }}
                                    const byteArray = new Uint8Array(byteNumbers);
                                    const blob = new Blob([byteArray], {{type: file.mime}});
                                    
                                    await writable.write(blob);
                                    await writable.close();
                                }}
                                statusDiv.innerText = "✅ File saved successfully!";
                                statusDiv.style.color = "green";
                            }} catch (err) {{
                                console.error(err);
                                statusDiv.innerText = "❌ Error: " + err.message;
                                statusDiv.style.color = "red";
                            }}
                        }} else {{
                            statusDiv.innerText = "⚠️ Browser doesn't support folder selection. Use the manual download button below.";
                        }}
                        
                        btn.disabled = false;
                        btn.innerText = "Save to Folder";
                    }}
                </script>
            </body>
            </html>
            """, height=150)

            st.divider()
            # Standard Streamlit Download Button as fallback/alternative
            st.download_button(
                label="Download Merged File (Standard)",
                data=file_data,
                file_name=output_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
