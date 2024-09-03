import pandas as pd
import re

def load_data(url):
    """Load the dataset from the specified URL."""
    return pd.read_excel(url)

def clean_data(df):
    """Clean and format the DataFrame."""
    # Handling null values
    df['Activity'] = df['Activity'].astype(str).fillna('Unknown Activity')
    df['Date'] = df['Date'].astype(str).fillna('Unknown Date')

    # Removing duplicates
    df.drop_duplicates(inplace=True)

    # Manipulating strings using Regex
    df['Activity'] = df['Activity'].apply(lambda x: re.sub(r'[^a-zA-Z\s]', '', str(x)))

    # Formatting data
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    # Handling date fields
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Renaming columns
    df.rename(columns={
        'Activity': 'Activity Description',
        'Date': 'Incident Date'
    }, inplace=True)

    return df

def style_table(df):
    """Apply styling to the DataFrame."""
    styled_df = df.style.set_properties(**{
        'background-color': 'white',
        'color': 'black',
        'border-color': 'black',
        'border-style': 'solid',
        'border-width': '1px',
        'text-align': 'left'
    }).set_table_styles([
        {'selector': 'thead th', 'props': [('background-color', 'lightgrey'), ('color', 'black'), ('font-weight', 'bold')]}
    ])
    return styled_df
