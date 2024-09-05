import pandas as pd

def rename_cols(df):        # Lo usé para nombres de cols
    
    df.rename(columns= lambda x : x.lower().replace(" ", "_"), inplace=True)
    return df


def remove_duplicates(df):

    df = df.dropna(subset=['country','name', 'sex', 'age', 'injury'])
    return df


def change_float_to_int(df):        # Lo usé para year
    df = df.apply(lambda x: x.fillna(0).astype(int) if x.dtype == 'float64' else x)
    return df


def remove_small_reps(df):
    for x in df.columns:
        if df[x].dtype == "str":
            df[x] = df[x].str.strip()
        df[x] = df[x].loc[df[x].isin(df[x].value_counts()[lambda x: x >= 30].index)]
    return df


def clean_str_punctuation(df):      # Lo use en country, state y location
    mytable = str.maketrans('', '', '¡¿.,!?;')
    
    for x in df.columns:

        df = df.str.strip().str.title().str.translate(mytable)

    return df


# BEA

def convert_decade(value):
    import re
    if isinstance(value, str):
        match = re.match(r"(\d+)s", value)
        if match:
            return int(match.group(1))
    return value


def convert_range(value):
    import re
    if isinstance(value, str):
        match = re.match(r"(\d+)\s*(or|\/)\s*(\d+)", value)
        if match:
            num1 = int(match.group(1))
            num2 = int(match.group(3))
            return (num1 + num2) / 2  
    return value


def fatal_injuries_renamed_FATAL(df):

    df = df.apply(lambda x: 'FATAL' if 'FATAL' in str(x).upper() else x)
    return df


# CARLOS

def clean_fatal_column(df):
    df = df.str.strip().str.upper().replace({
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
    df = df.apply(standardize_time)
    return df

# valid_species = {
#     'Tiger shark', 'White shark', 'Bull shark', 'Hammerhead shark', 'Great white shark', 
#     'Mako shark', 'Blacktip shark', 'Reef shark', 'Nurse shark', 'Whale shark', 'Tiger shark'
# }

def clean_species(species_str, valid_species):
    if pd.isna(species_str):
        return 'Unknown'
    species_str = str(species_str).strip()
    # Extract only the main species name
    for name in valid_species:
        if name.lower() in species_str.lower():
            return name
    return 'Unknown'  # Default value if no valid species name is found


# df['Species'] = df['Species'].apply(clean_species)


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
    df = df.apply(clean_pdf)
    return df


# ADRIÁN

def fix_original_order(df):
    
    df = df.apply(lambda x: str(x).replace('.0', '')).astype(int)
    return df


def main_cleaning(df_main):

    df_main = rename_cols(df_main)

    df_main = remove_duplicates(df_main)

    df_main = change_float_to_int(df_main)
    
    df_main = remove_small_reps(df_main)

    df_main = clean_str_punctuation(df_main)
    df_main = clean_str_punctuation(df_main)
    df_main = clean_str_punctuation(df_main)
    
    # df_main = fatal_injuries_renamed_FATAL(df_main, 'injury')
    # df_main = clean_fatal_column(df_main, 'fatal')
    # df_main = clean_time_column(df_main, 'time')
    
    # valid_species = {
    #     'Tiger shark', 'White shark', 'Bull shark', 'Hammerhead shark', 'Great white shark', 
    #     'Mako shark', 'Blacktip shark', 'Reef shark', 'Nurse shark', 'Whale shark', 'Tiger shark'
    # }
    # df_main['species'] = df_main['species'].apply(clean_species, valid_species=valid_species)
    
    # df_main = clean_pdf_column(df_main, 'pdf')
    # df_main = fix_original_order(df_main, 'original_order')
    
    return df_main

