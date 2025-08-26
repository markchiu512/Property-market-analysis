import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import matplotlib
from matplotlib.ticker import FuncFormatter


def load_multi_year_data():
    """Load and combine property data from 2022-2024"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    all_data = []
    years = ['2022', '2023', '2024']
    
    for year in years:
        raw_path = os.path.join(project_root, 'data', 'raw', f'pp-{year}.csv')
        print(f"Loading {year} data...")
        
        if os.path.exists(raw_path):
            # Load and clean data
            df = pd.read_csv(raw_path, header=None)
            df_clean = df[[1, 2, 3, 4, 5, 6, 11]].copy()
            df_clean.columns = ['Price', 'Date', 'Postcode', 'Property_Type', 
                               'New_built_indicator', 'Tenure_Type', 'City']
            
            # Clean date format
            df_clean['Date'] = df_clean['Date'].str.split(' ').str[0]
            df_clean['Date'] = pd.to_datetime(df_clean['Date'])
            
            # Create Postcode_Area
            df_clean['Postcode_Area'] = np.where(
                df_clean['Postcode'].str[1].str.isdigit(),
                df_clean['Postcode'].str[0],
                df_clean['Postcode'].str[:2])
            
            # Filter out unreasonably low prices
            df_clean = df_clean[df_clean['Price'] >= 30000]
            
            all_data.append(df_clean)
            print(f"Loaded {len(df_clean)} properties from {year}")
        else:
            print(f"Warning: {raw_path} not found")
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"Combined total: {len(combined_df)} properties from {len(all_data)} years (2022-2024)")
        return combined_df
    else:
        raise FileNotFoundError("No raw data files found")


def _format_price_k(x, pos):
    """Format price values to show in thousands (k)"""
    return f'£{x/1000:.0f}k'


def plot_price_by_postcode(df):
    """Create bar chart of average prices by postcode area"""
    # Calculate average prices by postcode area
    avg_prices = df.groupby('Postcode_Area')['Price'].mean().sort_values()
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    plt.bar(avg_prices.index, avg_prices.values)
    plt.title('Average Property Prices by Postcode Area')
    plt.xlabel('Postcode Area')
    plt.ylabel('Average Price (£)')
    plt.xticks(rotation=45)
    
    # Format y-axis to show prices in k format
    ax = plt.gca()
    ax.yaxis.set_major_formatter(FuncFormatter(_format_price_k))
    
    # Get the absolute path for saving
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    charts_dir = os.path.join(project_root, 'outputs', 'charts')
    
    # Ensure the charts directory exists
    os.makedirs(charts_dir, exist_ok=True)
    
    # Save the chart
    plt.tight_layout()
    chart_path = os.path.join(charts_dir, 'price_by_postcode.png')
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to: {chart_path}")
    
    # Only show if running in interactive mode
    if matplotlib.get_backend() != 'Agg':
        plt.show()
    plt.close()  # Close the figure to free memory


def plot_property_type_distribution(df):
    """Create pie chart of property types"""
    # Check if we have the right column name
    property_col = 'Property_Type' if 'Property_Type' in df.columns else 'Property Type'
    
    # Define mapping from codes to meaningful names
    property_type_mapping = {
        'D': 'Detached',
        'S': 'Semi-detached',
        'F': 'Flat/Apartment',
        'T': 'Terraced',
        'O': 'Other'
    }
    
    # Count property types and map to meaningful names
    counts = df[property_col].value_counts()
    labels = [property_type_mapping.get(code, f'Unknown ({code})') for code in counts.index]
    
    # Create the plot
    plt.figure(figsize=(10, 8))
    plt.pie(counts.values, labels=labels, autopct='%1.1f%%')
    plt.title('Distribution of Property Types')
    
    # Get the absolute path for saving
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    charts_dir = os.path.join(project_root, 'outputs', 'charts')
    
    # Ensure the charts directory exists
    os.makedirs(charts_dir, exist_ok=True)
    
    # Save the chart
    plt.tight_layout()
    chart_path = os.path.join(charts_dir, 'property_type_distribution.png')
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to: {chart_path}")
    
    # Only show if running in interactive mode
    if matplotlib.get_backend() != 'Agg':
        plt.show()
    plt.close()  # Close the figure to free memory

def _get_city_for_postcode(df, postcode):
    """Helper function to get city name for a given postcode"""
    city = df.loc[df['Postcode_Area'] == postcode, 'City'].unique()
    return city[0] if len(city) > 0 else None


def plot_london_price_by_property_type(df):
    """Create bar chart comparing London property prices by type"""
    # Property type mapping
    property_type_mapping = {
        'D': 'Detached',
        'S': 'Semi-detached',
        'F': 'Flat/Apartment',
        'T': 'Terraced',
        'O': 'Other'
    }
    
    # Calculate average prices by property type
    property_col = 'Property_Type' if 'Property_Type' in df.columns else 'Property Type'
    avg_prices = df.groupby(property_col)['Price'].mean().sort_values(ascending=False)
    
    # Map to full names
    labels = [property_type_mapping.get(code, f'Unknown ({code})') for code in avg_prices.index]
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    bars = plt.bar(labels, avg_prices.values)
    plt.title('Average Property Prices by Type - London')
    plt.xlabel('Property Type')
    plt.ylabel('Average Price (£)')
    plt.xticks(rotation=45)
    
    # Format y-axis to show prices in k format
    ax = plt.gca()
    ax.yaxis.set_major_formatter(FuncFormatter(_format_price_k))
    
    # Add value labels on bars in k format
    for bar, value in zip(bars, avg_prices.values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + value*0.01,
                f'£{value/1000:.0f}k', ha='center', va='bottom')
    
    # Get the absolute path for saving
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    charts_dir = os.path.join(project_root, 'outputs', 'charts')
    
    # Ensure the charts directory exists
    os.makedirs(charts_dir, exist_ok=True)
    
    # Save the chart
    plt.tight_layout()
    chart_path = os.path.join(charts_dir, 'london_price_by_property_type.png')
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to: {chart_path}")
    
    # Only show if running in interactive mode
    if matplotlib.get_backend() != 'Agg':
        plt.show()
    plt.close()  # Close the figure to free memory


def plot_london_postcode_prices(df):
    """Create bar chart of London property prices by postcode area"""
    # Calculate average prices by postcode area
    avg_prices = df.groupby('Postcode_Area')['Price'].mean().sort_values(ascending=False)
    
    # Create the plot
    plt.figure(figsize=(15, 8))
    bars = plt.bar(avg_prices.index, avg_prices.values)
    plt.title('Average Property Prices by London Postcode Area')
    plt.xlabel('Postcode Area')
    plt.ylabel('Average Price (£)')
    plt.xticks(rotation=45)
    
    # Format y-axis to show prices in k format
    ax = plt.gca()
    ax.yaxis.set_major_formatter(FuncFormatter(_format_price_k))
    
    # Add value labels on bars
    for bar, value in zip(bars, avg_prices.values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + value*0.01,
                f'£{value/1000:.0f}k', ha='center', va='bottom', fontsize=7)
    
    # Get the absolute path for saving
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    charts_dir = os.path.join(project_root, 'outputs', 'charts')
    
    # Ensure the charts directory exists
    os.makedirs(charts_dir, exist_ok=True)
    
    # Save the chart
    plt.tight_layout()
    chart_path = os.path.join(charts_dir, 'london_postcode_prices.png')
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to: {chart_path}")
    
    # Only show if running in interactive mode
    if matplotlib.get_backend() != 'Agg':
        plt.show()
    plt.close()  # Close the figure to free memory


def plot_london_sales_volume_by_month(df):
    """Plot monthly sales volume (transaction count) for London properties"""
    from data_filters import filter_london_properties
    
    # Filter to London properties
    london_df = filter_london_properties(df)
    
    # Extract month from Date column
    london_df['Month'] = london_df['Date'].dt.month
    london_df['Year'] = london_df['Date'].dt.year
    
    # Count transactions by month across all years
    monthly_counts = london_df.groupby('Month').size()
    
    # Month labels
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    bars = plt.bar(range(1, 13), monthly_counts.values)
    plt.title('London Property Sales Volume by Month (2022-2024)')
    plt.xlabel('Month')
    plt.ylabel('Number of Transactions')
    plt.xticks(range(1, 13), month_names)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + height*0.01,
                f'{int(height):,}', ha='center', va='bottom')
    
    # Get the absolute path for saving
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    charts_dir = os.path.join(project_root, 'outputs', 'charts')
    os.makedirs(charts_dir, exist_ok=True)
    
    plt.tight_layout()
    chart_path = os.path.join(charts_dir, 'london_sales_volume_by_month.png')
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    print(f"Monthly sales volume chart saved to: {chart_path}")
    
    # Print summary
    print(f"\nLondon Sales Volume Summary (2022-2024):")
    print(f"Total transactions: {london_df.shape[0]:,}")
    print(f"Highest month: {month_names[monthly_counts.idxmax()-1]} ({monthly_counts.max():,} transactions)")
    print(f"Lowest month: {month_names[monthly_counts.idxmin()-1]} ({monthly_counts.min():,} transactions)")
    
    if matplotlib.get_backend() != 'Agg':
        plt.show()
    plt.close()


def plot_london_sales_volume_by_year_month(df):
    """Plot monthly sales volume for London properties, showing each year separately"""
    from data_filters import filter_london_properties
    
    # Filter to London properties
    london_df = filter_london_properties(df)
    
    # Extract month and year from Date column
    london_df['Month'] = london_df['Date'].dt.month
    london_df['Year'] = london_df['Date'].dt.year
    
    # Count transactions by year and month
    yearly_monthly_counts = london_df.groupby(['Year', 'Month']).size().unstack(level=0, fill_value=0)
    
    # Month labels
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Create the plot
    plt.figure(figsize=(14, 8))
    
    # Plot each year as separate bars
    x = range(1, 13)
    width = 0.25
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Blue, Orange, Green
    
    for i, year in enumerate([2022, 2023, 2024]):
        if year in yearly_monthly_counts.columns:
            offset = (i - 1) * width
            bars = plt.bar([pos + offset for pos in x], yearly_monthly_counts[year], 
                          width=width, label=str(year), color=colors[i], alpha=0.8)
            
            # Add value labels on bars (only show if value > 0)
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    plt.text(bar.get_x() + bar.get_width()/2, height + height*0.01,
                            f'{int(height):,}', ha='center', va='bottom', fontsize=8)
    
    plt.title('London Property Sales Volume by Month - 3 Year Comparison')
    plt.xlabel('Month')
    plt.ylabel('Number of Transactions')
    plt.xticks(x, month_names)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    
    # Get the absolute path for saving
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    charts_dir = os.path.join(project_root, 'outputs', 'charts')
    os.makedirs(charts_dir, exist_ok=True)
    
    plt.tight_layout()
    chart_path = os.path.join(charts_dir, 'london_sales_volume_by_year_month.png')
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    print(f"Yearly comparison chart saved to: {chart_path}")
    
    # Print summary by year
    print(f"\nLondon Sales Volume by Year:")
    total_by_year = london_df.groupby('Year').size()
    for year in [2022, 2023, 2024]:
        if year in total_by_year.index:
            count = total_by_year[year]
            print(f"  {year}: {count:,} transactions")
            
            # Find peak month for this year
            if year in yearly_monthly_counts.columns:
                peak_month_num = yearly_monthly_counts[year].idxmax()
                peak_count = yearly_monthly_counts[year].max()
                print(f"    Peak month: {month_names[peak_month_num-1]} ({peak_count:,} transactions)")
    
    if matplotlib.get_backend() != 'Agg':
        plt.show()
    plt.close()
