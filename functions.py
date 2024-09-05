import pandas as pd

def rename_cols(df):
    """
    Renames all columns in the given DataFrame to lowercase and replaces spaces with underscores.
    
    Parameters:
        df (pandas.DataFrame): The DataFrame whose columns are to be renamed.
    
    Returns:
        pandas.DataFrame: The DataFrame with renamed columns.
    """
    
    df.rename(columns= lambda x : x.lower().replace(" ", "_"), inplace=True)
    return df


def remove_duplicates(df):
    """
    Remove rows with missing values in the specified columns and return the modified DataFrame.

    Parameters:
        df (pandas.DataFrame): The input DataFrame.

    Returns:
        pandas.DataFrame: The modified DataFrame with rows containing missing values in the specified columns removed.
    """

    df = df.dropna(subset=['country','name', 'sex', 'age', 'injury'])
    return df


def fill_NA(df):
    """
    Fill missing values in a DataFrame with 0 and convert the resulting values to integers.

    Parameters:
        df (pandas.DataFrame): The DataFrame to fill missing values in.

    Returns:
        pandas.DataFrame: The DataFrame with missing values filled with 0 and converted to integers.
    """
    
    df.fillna(0).astype(int)
    return df


def remove_small_reps(df):
    """
    Remove small representations from a DataFrame.

    Parameters:
        df (pandas.Series): The input Series.

    Returns:
        pandas.Series: The Series with small representations removed.
    """
    df = df.str.strip()
    df = df.loc[df.isin(df.value_counts()[lambda x: x >= 30].index)]    
    return df


def clean_str_punctuation(df):
    """
    Cleans a pandas DataFrame by removing punctuation, stripping whitespace, and title-casing strings.

    Parameters:
        df (pandas.DataFrame): The DataFrame to be cleaned.

    Returns:
        pandas.DataFrame: The cleaned DataFrame.
    """
    mytable = str.maketrans('', '', '¡¿.,!?;')

    df = df.str.strip().str.title().str.translate(mytable)

    return df


# BEA

def convert_decade(value):
    """
    Converts a decade string to its corresponding integer value.

    Parameters:
        value (str or int): The decade string or integer to be converted.

    Returns:
        int: The integer value of the decade, or the original value if it's not a string.
    """
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
    """
    Cleans and standardizes the 'Fatal' column in a given DataFrame.

    Parameters:
        df (pandas.DataFrame): The DataFrame containing the 'Fatal' column to be cleaned.

    Returns:
        pandas.DataFrame: The DataFrame with the 'Fatal' column cleaned and standardized.
    """
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
    """
    Standardizes a given time string into a 24-hour format.

    Parameters:
        time_str (str or int): The time string to be standardized.

    Returns:
        str: The standardized time string in 24-hour format.
    """
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
    """
    Cleans a pandas DataFrame by applying the standardize_time function to each element.

    Parameters:
        df (pandas DataFrame): The DataFrame to be cleaned.

    Returns:
        pandas DataFrame: The cleaned DataFrame.
    """
    df = df.apply(standardize_time)
    return df

# valid_species = {
#     'Tiger shark', 'White shark', 'Bull shark', 'Hammerhead shark', 'Great white shark', 
#     'Mako shark', 'Blacktip shark', 'Reef shark', 'Nurse shark', 'Whale shark', 'Tiger shark'
# }

def clean_species(species_str, valid_species):
    """
    Cleans a string representing a species by comparing it to a list of valid species names.

    Parameters:
        species_str (str): The string to be cleaned.
        valid_species (list): A list of valid species names.

    Returns:
        str: The cleaned species name. If the input string is empty or None, returns 'Unknown'.
    """
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
    """
    Cleans a string representing a PDF by removing any non-alphanumeric characters except periods, underscores, and dashes.
    
    Parameters:
        pdf_str (str or int): The string or integer to be cleaned.
        
    Returns:
        str: The cleaned string. If the input string is empty or None, returns 'Unknown'.
    """
    if pd.isna(pdf_str):
        return 'Unknown'
    if isinstance(pdf_str, int):
        pdf_str = str(pdf_str)
    pdf_str = str(pdf_str).strip()
    # Remove any non-alphanumeric characters except periods, underscores, and dashes
    pdf_str = ''.join(c for c in pdf_str if c.isalnum() or c in ['.', '_', '-'])
    return pdf_str if pdf_str else 'Unknown'


def clean_pdf_column(df):
    """
    Cleans a pandas DataFrame by applying the clean_pdf function to each element.

    Parameters:
        df (pandas DataFrame): The DataFrame to be cleaned.

    Returns:
        pandas DataFrame: The cleaned DataFrame.
    """
    df = df.apply(clean_pdf)
    return df


# ADRIÁN

def fix_original_order(df):
    """
    Fixes the 'original order' column in a DataFrame by removing trailing '.0' from the values and converting them to integers.

    Parameters:
        df (pandas DataFrame): The DataFrame containing the 'original order' column to be fixed.

    Returns:
        pandas DataFrame: The DataFrame with the 'original order' column fixed.
    """
    
    df = df.apply(lambda x: str(x).replace('.0', '')).astype(int)
    return df


def main_cleaning(df_main):
	
    """
	Main data cleaning function.

	Parameters:
		df_main (pandas DataFrame): The main DataFrame to be cleaned.

	Returns:
		pandas DataFrame: The cleaned DataFrame.
	"""

    df_main = rename_cols(df_main)

    df_main = remove_duplicates