import pandas as pd

def rename_cols(df):
    """
    Renames the DataFrame columns to improve clarity and consistency.
    In this case, the function performs two renaming operations:

    1. Renames specific columns, such as 'Unnamed: 11' to 'fatal' and 'Species ' to 'species'. 
       The 'fatal' column will be our reference point for identifying fatal injuries.
    
    2. Converts all column names to lowercase and replaces spaces with underscores.
       This step standardizes the column names, making it easier to work with them.

    Parameters:
        df (pandas.DataFrame): The DataFrame whose columns will be renamed.

    Returns:
        pandas.DataFrame: The DataFrame with renamed columns.
    """
    
    # Rename specific columns for clarity
    df.rename(columns={"Unnamed: 11": "fatal", "Species ": "species"}, inplace=True)
    
    # Convert the rest of the column names to lowercase and replace spaces with underscores.
    df.rename(columns=lambda x: x.lower().replace(" ", "_"), inplace=True)
    
    return df


def remove_duplicates(df):
    """
    Removes rows with missing values in key columns for our analysis and returns the modified DataFrame.
    This step eliminates rows where data is missing in essential columns such as 'country', 'name', 'sex', 'age',
    and 'fatal'.

    Parameters:
        df (pandas.DataFrame): The input DataFrame.

    Returns:
        pandas.DataFrame: The modified DataFrame, without rows that have missing values in key columns.
    """
    df = df.dropna(subset=['country','name', 'sex', 'age', 'fatal'])
    return df


def change_float_to_int(df):
    """
    Converts float64 columns to their integer equivalents.
    Since some numeric columns, such as 'age' or 'year', are stored as floats due to the presence of null values or 
    decimals, this function converts them to integers as decimals are not relevant. Null values are handled by assigning 
    them 0 to prevent errors in later calculations.

    Parameters:
        df (pandas.DataFrame): The DataFrame to modify.

    Returns:
        pandas.DataFrame: The modified DataFrame with float64 columns converted to integers.
    """
    df = df.apply(lambda x: x.fillna(0).astype(int) if x.dtype == 'float64' else x)
    return df


def remove_small_reps(df):
    """
    Removes small representations from each column, keeping only those that have at least 30 occurrences.
    This function reviews all columns and focuses on string-type columns.
    
    First, it removes unnecessary leading and trailing spaces from strings. Then, 
    it filters rows in each column, retaining only those that appear at least 30 times in the column.
    This is useful for removing low-representation values that might skew the analysis.

    Parameters:
        df (pandas.DataFrame): The DataFrame to process.

    Returns:
        pandas.DataFrame: The DataFrame with small representations removed and text formatting corrected.
    """
    for x in df.columns:
        if df[x].dtype == "str":  # If the column is of string type, remove leading and trailing spaces.
            df[x] = df[x].str.strip()
        # Filter the column to keep only values that appear at least 30 times.
        df[x] = df[x].loc[df[x].isin(df[x].value_counts()[lambda x: x >= 30].index)]
    return df


def clean_str_punctuation(df):
    """
    Cleans by removing punctuation, adjusting white spaces, and applying title case to text strings. 
    This function is used in columns such as 'country', 'state', and 'location'.

    First, a translation table is created to remove common punctuation characters like commas, periods, 
    exclamation marks, and question marks. Then, the function iterates over each column in the DataFrame, 
    and if the column is of string type, it performs the transformations.

    Parameters:
        df (pandas.DataFrame): The DataFrame to clean.

    Returns:
        pandas.DataFrame: The DataFrame with formatted text strings and no punctuation.
    """
    # Define the punctuation characters to be removed.
    mytable = str.maketrans('', '', '¡¿.,!?;')
    
    # Iterate through each column and apply the cleaning only to 'object' type (text) columns.
    for x in df.columns:
        if df[x].dtype == "object":  # If the column is of string type.
            df[x] = df[x].str.strip().str.title().str.translate(mytable)
    
    # Create a subset of string-type columns and apply the same cleaning.
    df_clean = df.select_dtypes(include=['object'])
    df_clean = df_clean.apply(lambda x: x.str.strip().str.title().str.translate(mytable))
    
    # Replace the original columns with the cleaned ones.
    df = df.drop(df_clean.columns, axis=1).join(df_clean)
    
    return df


# BEA

def convert_decade(df):
    """
    Converts a string representing a decade into its corresponding numeric value.

    This function converts text expressing decades (e.g., '1990s') into an integer value
    to facilitate analysis.

    Parameters:
        df (str or int): The string representing a decade, or a value that doesn't require conversion.

    Returns:
        int or original: The decade value as an integer, or the original value if it is not a valid decade string.
    """
    import re
    if isinstance(df, str):  # Check if the input is a string.
        # Use a regular expression to search for the format 'XXXXs' (e.g., '1990s').
        match = re.match(r"(\d+)s", df)
        if match:
            return int(match.group(1))  # Convert the decade to an integer.
    return df  # Return the original value if the condition is not met.


def convert_range(df):
    """
    Converts number ranges expressed in text into their average.

    Some columns may contain ranges such as '20-30' or '15/25'. This function takes these values 
    and converts them into the average to provide a single representation of the range. This is especially 
    useful for normalizing the 'age' column.

    Parameters:
        value (str): The string representing a numeric range.

    Returns:
        float: The average value of the range, or the original value if it is not a range.
    """
    import re
    if isinstance(df, str):
        match = re.match(r"(\d+)\s*(or|\/)\s*(\d+)", df)
        if match:
            num1 = int(match.group(1))
            num2 = int(match.group(3))
            return (num1 + num2) / 2  
    return df


# CARLOS

def clean_fatal_column(df):
    """
    Cleans and standardizes the 'fatal' column.
    This function performs the following transformations:
    
    1. Removes white spaces and applies uppercase formatting: Removes unnecessary white spaces 
       and converts all text to uppercase.
    2. Standardizes the different ways fatality is recorded, converting:
       - 'Y', 'F', and 'Y X 2' to 'Yes'.
       - 'N', 'N N' to 'No'.
       - Ambiguous values such as 'M', 'NQ', and 'UNKNOWN' to 'Unknown'.
    3. Missing or null values in the column are replaced with 'Unknown'.

    Parameters:
        df (pandas.DataFrame): The DataFrame containing the 'fatal' column to clean.

    Returns:
        pandas.DataFrame: The DataFrame with the 'fatal' column cleaned and standardized.
    """
    
    # Clean white spaces, convert to uppercase, and replace specific values
    df["fatal"] = df["fatal"].str.strip().str.upper().replace({
        'Y': 'Yes',  # Convert 'Y' to 'Yes'
        'N': 'No',  # Convert 'N' to 'No'
        'F': 'Yes',  # Convert 'F' to 'Yes' (presumably indicates fatality)
        'N N': 'No',  # Correct variations of 'No'
        'UNKNOWN': 'Unknown',  # Standardize 'Unknown'
        'M': 'Unknown',  # Assume 'M' means 'Unknown'
        'NQ': 'Unknown',  # Assume 'NQ' means 'Unknown'
        'Y X 2': 'Yes'  # Assume 'Y X 2' means 'Yes'
    })
    
    # Fill missing values with 'Unknown'
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
    
    df_main = clean_fatal_column(df_main)
    df_main = clean_time_column(df_main)
    

    df_main = clean_species_column(df_main, valid_species)
    
    df_main = clean_pdf_column(df_main)
    df_main = drop_useless_columns(df_main)
    
    return df_main