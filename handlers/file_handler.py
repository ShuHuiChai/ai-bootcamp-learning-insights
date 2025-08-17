import streamlit as st
import pandas as pd
import zipfile
import io
import os
import csv
from datetime import datetime


def is_valid_zip_file(uploaded_file):
    """
    Checks if the uploaded file is a valid ZIP file according to specific rules:
    1. Filename has 4 parts delimited by '_'.
    2. Last part of filename is a valid YYYYMMDD date.
    3. ZIP contains exactly one CSV file.
    """
    if uploaded_file is None:
        return False, "No file uploaded."

    file_name = uploaded_file.name

    name_parts = file_name.replace('.zip', '').split('_')
    date_string = name_parts[-1]
    try:
        datetime.strptime(date_string, '%Y%m%d')
    except ValueError:
        return False

    try:
        zip_buffer = io.BytesIO(uploaded_file.getvalue())
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            csv_files = [name for name in zf.namelist() if name.endswith('.csv')]

            if len(csv_files) == 0:
                return False
            elif len(csv_files) > 1:
                return False

            return True

    except Exception as e:
        return False, f"Error: {e}"

def process_zip_files(uploaded_files_info):
        
    dataframe = pd.DataFrame(columns=['Attempt Date', 'Form Class', 'Index Number', 'Name', 'Percentage', 'Assignment'])
    
    for file_info in uploaded_files_info:
        file_name = file_info['name']
        file_content = file_info['content']
        try:
            with zipfile.ZipFile(io.BytesIO(file_content), 'r') as zf:
                csv_files = [name for name in zf.namelist() if name.endswith('.csv')]
                if not csv_files:
                    st.error(f"Internal error: No CSV found in '{file_name}'.")
                    continue

                with zf.open(csv_files[0]) as csv_file:
                    csv_content = csv_file.read().decode('utf-8')
                    with io.StringIO(csv_content) as f:
                        df = process_csv_content(f)
                        df['Assignment'] = csv_file.name.replace('.csv', '')
                        dataframe = pd.concat([dataframe, df])

        except Exception as e:
            st.error(f"Error processing ZIP file '{file_name}': {e}")
    
    dataframe = dataframe.drop_duplicates()
    return dataframe


def process_csv_content(f):
    """
    Reads the csv content of the file and reorganises it according to the following columns:
    'Attempt Date', 'Form Class', 'Index Number', 'Name', 'Percentage'
    """

    reader = csv.reader(f, delimiter=',', quotechar='"', lineterminator='\n')
    
    marks_per_question = []
    for i, row in enumerate(reader):
        if i < 3: # skip the first three rows
            continue
        elif i == 3: # fourth row contains marks per question
            marks_per_question = row
        elif i == 4: # fifth row contains column headers
            data_df = pd.DataFrame(columns=row)
        else: # subsequent rows contain data
            data_df.loc[i-5] = row
        
    data_df.iloc[:, 4:] = data_df.iloc[:, 4:].apply(pd.to_numeric, errors='coerce') # force numeric conversion for question columns
    data_df['Total Score'] = data_df.iloc[:,4:].sum(axis=1)
    total_marks = sum_list(marks_per_question[4:])
    data_df['Percentage'] = data_df['Total Score'] / total_marks
    data_df = data_df.drop(data_df.iloc[:, 4:-1].columns, axis=1) # drop all question columns and Total Score column; keep only metadata columns and Percentage column

    return data_df
    

def sum_list(marks:list):
    # sum marks in list of strings
    total_marks = 0
    for elem in marks:
        if elem == '':
            continue
        else:
            total_marks += int(elem)
    
    return total_marks