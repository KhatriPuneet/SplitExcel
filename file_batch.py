import pandas as pd
import math
import os
from datetime import datetime


def get_unique_date_dir(base_path):
    """
    Creates a directory with the current date (e.g., '11 Dec') inside base_path.
    If it exists, adds a numeric suffix (e.g., '11 Dec 1', '11 Dec 2').
    Returns the full path to the created directory.
    """
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    date_label = datetime.now().strftime("%d %b")
    target_dir = os.path.join(base_path, date_label)
    
    counter = 1
    original_target = target_dir
    while os.path.exists(target_dir):
        target_dir = f"{original_target} {counter}"
        counter += 1
        
    os.makedirs(target_dir)
    return target_dir, date_label


def process_file(file_obj, output_dir, date_label, rows_per_file=5000, prefix="B"):
    # Read Excel (works with file path or file-like object)
    df = pd.read_excel(file_obj)
    total_rows = len(df)
    
    num_files = math.ceil(total_rows / rows_per_file)
    
    generated_files = []
    
    for i in range(num_files):
        start = i * rows_per_file
        end = start + rows_per_file
        chunk = df.iloc[start:end]
        
        filename = f"{prefix}{i+1} - {date_label} 5k.csv"
        file_path = os.path.join(output_dir, filename)
        
        chunk.to_csv(file_path, index=False)
        generated_files.append(file_path)
        
    return generated_files

if __name__ == "__main__":
    # ---- SETTINGS ----
    input_file = "your_file.xlsx"   # change this
    rows_per_file = 5000
    prefix = "B"                    # B1, B2, B3...
    base_output_path = "/Users/Puneetkhatri/Documents/Daily Work"
    # -------------------
    
    try:
        # 1. Setup output directory
        output_dir, date_label = get_unique_date_dir(base_output_path)
        print(f"Saving files to: {output_dir}")

        # 2. Process
        files = process_file(input_file, output_dir, date_label, rows_per_file, prefix)
        print(f"Done! Created {len(files)} files.")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
