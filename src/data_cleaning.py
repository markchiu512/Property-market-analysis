import pandas as pd
import numpy as np


def clean_price_data(df):
    """
    Clean price data by removing unreasonably low prices (likely data errors).

    Args:
        df: DataFrame with Price column

    Returns:
        DataFrame with cleaned prices
    """
    original_count = len(df)

    # Remove properties with unreasonably low prices (likely data entry errors)
    # Keep all high prices as London/luxury properties can be very expensive
    df_clean = df[df['Price'] >= 30000].copy()  # Remove prices below £30,000

    removed_count = original_count - len(df_clean)
    if removed_count > 0:
        print(f"Removed {removed_count} properties with unreasonably low "
              f"prices (< £30,000)")

    return df_clean


def load_data(dataset='auto'):
    """
    Load property data from processed files.

    Args:
        dataset (str): 'synthetic', 'real', 'sample', or 'auto' (default)
                      'auto' tries real first, falls back to synthetic
    """
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    if dataset == 'auto':
        # Try real data first, fall back to synthetic
        real_path = os.path.join(project_root, 'data', 'processed',
                                 'property_data_real.csv')
        if os.path.exists(real_path):
            dataset = 'real'
        else:
            dataset = 'synthetic'

    if dataset == 'synthetic':
        csv_path = os.path.join(project_root, 'data', 'processed',
                                'property_data_synthetic.csv')
        data_type = "synthetic"
    elif dataset == 'real':
        csv_path = os.path.join(project_root, 'data', 'processed',
                                'property_data_real.csv')
        data_type = "real"
    elif dataset == 'sample':
        csv_path = os.path.join(project_root, 'data', 'samples',
                                'property_data_real_sample.csv')
        data_type = "real sample"
    else:
        raise ValueError("Dataset must be 'synthetic', 'real', 'sample', "
                         "or 'auto'")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} {data_type} properties from CSV")

    # Clean price data for real datasets only
    if dataset in ['real', 'sample'] and 'synthetic' not in data_type:
        df = clean_price_data(df)
        print(f"After cleaning: {len(df)} properties remain")

    return df


def clean_pp_data():
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    raw_path = os.path.join(project_root, 'data', 'raw', 'pp-2024.csv')

    print("Loading raw property data (this may take a moment...)")
    df_pp = pd.read_csv(raw_path, header=None)
    print(f"Loaded {len(df_pp)} raw property records")

    df_clean = df_pp[[1, 2, 3, 4, 5, 6, 11]].copy()
    df_clean.columns = ['Price', 'Date', 'Postcode', 'Property_Type',
                        'New_built_indicator', 'Tenure_Type', 'City']

    df_clean['Date'] = df_clean['Date'].str.split(' ').str[0]

    df_clean['Postcode_Area'] = np.where(
        df_clean['Postcode'].str[1].str.isdigit(),
        df_clean['Postcode'].str[0],
        df_clean['Postcode'].str[:2])

    # Save full dataset
    processed_path = os.path.join(project_root, 'data', 'processed',
                                  'property_data_real.csv')
    df_clean.to_csv(processed_path, index=False)
    print(f"Saved {len(df_clean)} cleaned properties to "
          f"property_data_real.csv")

    # Create sample for demo/testing (5000 records)
    sample_df = df_clean.sample(n=min(5000, len(df_clean)), random_state=42)
    sample_path = os.path.join(project_root, 'data', 'samples',
                               'property_data_real_sample.csv')
    sample_df.to_csv(sample_path, index=False)
    print(f"Created sample with {len(sample_df)} records for demo purposes")

    return df_clean
