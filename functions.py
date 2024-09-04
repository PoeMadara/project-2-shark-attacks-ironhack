import subprocess
import sys
import pandas as pd

def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError:
        print(f"Failed to install {package}. Please install it manually.")

# Install necessary packages
install('requests')
install('openpyxl')  # Ensure openpyxl is installed

import requests

def download_excel(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)

def load_excel(filename):
    return pd.read_excel(filename)

def rename_columns(df):
    return df.rename(columns={'Unnamed: 11': 'Fatal', 'Species ': 'Species', 'Source': 'Source', 'pdf': 'PDF'})

def clean_fatal_column(df):
    df['Fatal'] = df['Fatal'].str.strip().str.upper().replace({
        'Y': 'Yes',
        'N': 'No',
        'F': 'Yes',
        'N N': 'No',
        'UNKNOWN': 'Unknown',
        'M': 'Unknown',  # Assuming 'M' means 'Unknown'
        'NQ': 'Unknown',  # Assuming 'NQ' means 'Unknown'
        'Y X 2': 'Yes'  # Assuming 'Y X 2' means 'Yes'
    })
    df['Fatal'] = df['Fatal'].fillna('Unknown')
    return df

def standardize_time(time_str):
    if pd.isna(time_str):
        return '12:00'
    if isinstance(time_str, int):
        time_str = str(time_str)
    time_str = time_str.strip().lower()
    
    # Handle various time descriptions
    if 'early' in time_str or 'dawn' in time_str or 'before' in time_str:
        return '06:00'
    if 'morning' in time_str:
        return '09:00'
    if 'midday' in time_str or 'noon' in time_str:
        return '12:00'
    if 'afternoon' in time_str:
        return '15:00'
    if 'evening' in time_str or 'dusk' in time_str or 'sunset' in time_str:
        return '18:00'
    if 'night' in time_str or 'midnight' in time_str:
        return '23:00'
    
    # Try to parse times in different formats
    try:
        time_str = time_str.replace('h', ':').replace(' ', '')
        if '-' in time_str:
            time_str = time_str.split('-')[0].strip()
        if ':' in time_str:
            return pd.to_datetime(time_str, format='%H:%M', errors='coerce').strftime('%H:%M')
        if ' ' in time_str:
            time_str = time_str.split()[0]
        time_str = time_str.replace('j', '').replace('"', '').replace('pm', '').replace('am', '')
        if len(time_str) == 4:
            return f'{time_str[:2]}:{time_str[2:]}'
        if len(time_str) == 3:
            return f'0{time_str[0]}:{time_str[1:]}'
        return '12:00'  # Default value if parsing fails
    except:
        return '12:00'

def clean_time_column(df):
    df['Time'] = df['Time'].apply(standardize_time)
    return df

valid_species = {
    'Tiger shark', 'White shark', 'Bull shark', 'Hammerhead shark', 'Great white shark', 
    'Mako shark', 'Blacktip shark', 'Reef shark', 'Nurse shark', 'Whale shark', 'Tiger shark'
}

def clean_species(species_str):
    if pd.isna(species_str):
        return 'Unknown'
    species_str = str(species_str).strip()
    # Extract only the main species name
    for name in valid_species:
        if name.lower() in species_str.lower():
            return name
    return 'Unknown'  # Default value if no valid species name is found

def clean_species_column(df):
    df['Species'] = df['Species'].apply(clean_species)
    return df

def clean_source_column(df):
    df['Source'] = df['Source'].str.strip().replace({'UNKNOWN': 'Unknown'})
    return df

def clean_pdf(pdf_str):
    if pd.isna(pdf_str):
        return 'Unknown'
    if isinstance(pdf_str, int):
        pdf_str = str(pdf_str)
    pdf_str = str(pdf_str).strip()
    # Remove any non-alphanumeric characters except periods, underscores, and dashes
    pdf_str = ''.join(c for c in pdf_str if c.isalnum() or c in ['.', '_', '-'])
    return pdf_str if pdf_str else 'Unknown'

def clean_pdf_column(df):
    df['PDF'] = df['PDF'].apply(clean_pdf)
    return df

def save_excel(df, filename):
    df.to_excel(filename, index=False)
