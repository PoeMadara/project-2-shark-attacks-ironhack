import pandas as pd
import re

def load_data(url):
    """Load the dataset from the specified URL."""
    return pd.read_excel(url)

def clean_data(df_sa):
    """Clean and format the DataFrame."""
    # Handling null values
    df_sa['Activity'] = df_sa['Activity'].astype(str).fillna('Unknown Activity')
    df_sa['Date'] = df_sa['Date'].astype(str).fillna('Unknown Date')

    # Removing duplicates
    df_sa.drop_duplicates(inplace=True)

    # Manipulating strings using Regex
    df_sa['Activity'] = df_sa['Activity'].apply(lambda x: re.sub(r'[^a-zA-Z\s]', '', str(x)))

    # Formatting data
    df_sa = df_sa.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    # Handling date fields
    if 'Date' in df_sa.columns:
        df_sa['Date'] = pd.to_datetime(df_sa['Date'], errors='coerce')

    # Renaming columns
    df_sa.rename(columns={
        'Activity': 'Activity Description',
        'Date': 'Incident Date'
    }, inplace=True)

    return df_sa

def style_table(df_sa):
    """Apply styling to the DataFrame."""
    styled_df = df_sa.style.set_properties(**{
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
