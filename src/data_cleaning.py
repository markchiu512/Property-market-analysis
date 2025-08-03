import pandas as pd
import numpy as np

def load_data():
    df = pd.read_csv('../data/processed/property_data.csv')
    print(f"Loaded {len(df)} properties from CSV")
    return df

def clean_pp_data():
    df_pp = pd.read_csv('../data/raw/pp-2024.csv', header=None)

    df_clean = df_pp[[1, 2, 3, 4, 5, 6]].copy()
    df_clean.columns = ['Price', 'Date', 'Postcode', 'Property_Type', 'New_built_indicator', 'Tenure_Type']

    df_clean['Date'] = df_clean['Date'].str.split(' ').str[0]

    df_clean['Postcode_Area'] = np.where(
    df_clean['Postcode'].str[1].str.isdigit(),  
    df_clean['Postcode'].str[0],               
    df_clean['Postcode'].str[:2])

    df_clean.to_csv('../data/processed/property_data.csv', index=False)
    return  df_clean



if __name__ == "__main__":
    df = clean_pp_data()
    print(df)

