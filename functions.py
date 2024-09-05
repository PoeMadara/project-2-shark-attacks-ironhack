import pandas as pd

def rename_cols(df):        

    df.rename(columns={"Unnamed: 11" : "fatal", "Species " : "species"}, inplace=True)
    df.rename(columns= lambda x : x.lower().replace(" ", "_"), inplace=True)
    
    return df


def remove_duplicates(df):

    df = df.dropna(subset=['country','name', 'sex', 'age', 'fatal'])
    return df


def change_float_to_int(df):       
    df = df.apply(lambda x: x.fillna(0).astype(int) if x.dtype == 'float64' else x)
    return df


def remove_small_reps(df):
    for x in df.columns:
        if df[x].dtype == "str":
            df[x] = df[x].str.strip()
            df[x] = df[x].loc[df[x].isin(df[x].value_counts()[lambda x: x >= 30].index)]
        
    return df


def clean_str_punctuation(df):

    mytable = str.maketrans('', '', '¡¿.,!?;')
    for x in df.columns:
        if df[x].dtype == "object":
            df[x] = df[x].str.strip().str.title().str.translate(mytable)
    df_clean = df.select_dtypes(include=['object'])
    df_clean = df_clean.apply(lambda x: x.str.strip().str.title().str.translate(mytable))
    df = df.drop(df_clean.columns, axis=1).join(df_clean)
    return df


def clean_age_column(df):
    import numpy as np

    df["age"] = df["age"].str.split(" ").str[0].apply(pd.to_numeric, errors="coerce")
    df["age"].fillna(value=np.nan, inplace=True)
    
    return df


            

# def convert_decade(df):
#     import re
#     if isinstance(df["age"], str):
#         match = re.match(r"(\d+)s", df)
#         if match:
#             return int(match.group(1))
#     return df


# def convert_range(df):
#     import re
#     if isinstance(df["age"], str):
#         match = re.match(r"(\d+)\s*(or|\/)\s*(\d+)", df)
#         if match:
#             num1 = int(match.group(1))
#             num2 = int(match.group(3))
#             return (num1 + num2) / 2  
#     return df


# CARLOS

def clean_fatal_column(df):
    df["fatal"] = df["fatal"].str.strip().str.upper().replace({
        'Y': 'Yes',
        'N': 'No',
        'F': 'Yes',
        'N N': 'No',
        'UNKNOWN': 'Unknown',
        'M': 'Unknown',  # Assuming 'M' means 'Unknown'
        'NQ': 'Unknown',  # Assuming 'NQ' means 'Unknown'
        'Y X 2': 'Yes'  # Assuming 'Y X 2' means 'Yes'
    })
    df['fatal'] = df['fatal'].fillna('Unknown')
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
    df["time"] = df["time"].apply(standardize_time)
    return df


valid_species = {
    'Tiger shark', 'White shark', 'Bull shark', 'Hammerhead shark', 'Great white shark', 
    'Mako shark', 'Blacktip shark', 'Reef shark', 'Nurse shark', 'Whale shark', 'Tiger shark'
}


def clean_species(species_str, valid_species):

    if pd.isna(species_str):
        return 'Unknown'
    species_str = str(species_str).strip()
    # Extract only the main species name
    for name in valid_species:
        if name.lower() in species_str.lower():
            return name
    return 'Unknown'  # Default value if no valid species name is found


def clean_species_column(df, valid_species):
    df['species'] = df['species'].apply(lambda x: clean_species(x, valid_species))
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
    df['pdf'] = df['pdf'].apply(clean_pdf)
    return df


def drop_useless_columns(df):
    df = df.drop(["original_order", "unnamed:_21", "unnamed:_22"], axis=1)
    return df


def main_cleaning(df_main, valid_species):

    
    df_main = rename_cols(df_main)

    df_main = remove_duplicates(df_main)

    df_main = change_float_to_int(df_main)
    
    df_main = remove_small_reps(df_main)

    df_main = clean_str_punctuation(df_main)
    df_main = clean_str_punctuation(df_main)
    df_main = clean_str_punctuation(df_main)

    df_main = clean_age_column(df_main)
    
    df_main = clean_fatal_column(df_main)
    df_main = clean_time_column(df_main)
    

    df_main = clean_species_column(df_main, valid_species)
    
    df_main = clean_pdf_column(df_main)
    df_main = drop_useless_columns(df_main)
    
    return df_main

