import pandas as pd


# London postcode areas (comprehensive list)
LONDON_POSTCODES = {
    # Central London
    'EC', 'WC', 'E', 'N', 'NW', 'SE', 'SW', 'W',
    # Greater London areas
    'BR', 'CR', 'DA', 'EN', 'HA', 'IG', 'KT', 'RM', 'SM', 'TW', 'UB', 'WD'
}


def filter_london_properties(df):
    """
    Filter dataframe to include only London properties based on postcode areas.
    
    Args:
        df: DataFrame with property data including 'Postcode_Area' column
        
    Returns:
        DataFrame: Filtered dataframe with only London properties
    """
    london_df = df[df['Postcode_Area'].isin(LONDON_POSTCODES)].copy()
    print(f"Filtered to {len(london_df)} London properties from {len(df)} total properties")
    return london_df


def filter_by_postcode_areas(df, postcode_areas):
    """
    Filter dataframe by specific postcode areas.
    
    Args:
        df: DataFrame with property data
        postcode_areas: List or set of postcode areas to include
        
    Returns:
        DataFrame: Filtered dataframe
    """
    filtered_df = df[df['Postcode_Area'].isin(postcode_areas)].copy()
    print(f"Filtered to {len(filtered_df)} properties in areas: {', '.join(postcode_areas)}")
    return filtered_df


def filter_central_london_properties(df):
    """
    Filter to Central London postcodes only (EC, WC, E, N, NW, SE, SW, W).
    
    Args:
        df: DataFrame with property data
        
    Returns:
        DataFrame: Filtered dataframe with only Central London properties
    """
    central_london_postcodes = {'EC', 'WC', 'E', 'N', 'NW', 'SE', 'SW', 'W'}
    central_df = df[df['Postcode_Area'].isin(central_london_postcodes)].copy()
    print(f"Filtered to {len(central_df)} Central London properties")
    return central_df


def get_london_property_stats(df):
    """
    Get summary statistics for London properties.
    
    Args:
        df: DataFrame with property data (should be pre-filtered to London)
        
    Returns:
        dict: Dictionary with various statistics
    """
    stats = {
        'total_properties': len(df),
        'avg_price': df['Price'].mean(),
        'median_price': df['Price'].median(),
        'min_price': df['Price'].min(),
        'max_price': df['Price'].max(),
        'property_type_counts': df['Property_Type'].value_counts().to_dict(),
        'postcode_areas': df['Postcode_Area'].nunique(),
        'avg_price_by_type': df.groupby('Property_Type')['Price'].mean().to_dict()
    }
    return stats