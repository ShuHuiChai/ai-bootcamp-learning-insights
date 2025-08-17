import streamlit as st
import zipfile
from datetime import datetime
import os

TEMPDIR = "tempdir"
def process_zip_files(uploaded_files):
    """
    Process the uploaded zip files and extract their contents.
    
    Args:
        uploaded_files (list): List of uploaded zip file objects.
    
    Returns:
        list: List of extracted file paths.
    """
    print("Processing zip files...")
    valid_files = []
    invalid_files = []
    extracted_files = []

    for uploaded_file in uploaded_files:
        # Check if the uploaded file is a valid zip file
        filename = uploaded_file.name[0:-4]  # remove .zip extension from name
        filename_list = filename.split('_')
        
        if len(filename_list) == 4 and filename_list[0] == 'Marks' and is_date(filename_list[3]):

            filepath = os.path.join('TEMPDIR', uploaded_file.name)

            # Temporarily save zip file to tempzips folder
            with open(filepath, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Check if it is a valid file: filename with four components, has valid date, and only one .csv file inside
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                valid_files.append(uploaded_file.name)
                zip_ref.extractall("extracted_files")
                # extracted_files.extend(zip_ref.namelist())
        else:
            invalid_files.append(uploaded_file.name)
            continue

    return valid_files, invalid_files


def is_date(filedate:str):
    """
    Check that string is a valid date
    
    Args:
        filedate: string to check
    
    Returns:
        True or False
    """

    try:
        if datetime.strptime(filedate, '%Y%m%d'):
            return True
        else:
            return False
    except ValueError:
        return False
