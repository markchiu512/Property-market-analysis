import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import matplotlib
from matplotlib.ticker import FuncFormatter


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
    
    # Add value labels on bars (only for top values to avoid clutter)
    for i, (bar, value) in enumerate(zip(bars, avg_prices.values)):
        if i < 10:  # Only label top 10
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + value*0.01,
                    f'£{value/1000:.0f}k', ha='center', va='bottom', fontsize=8)
    
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

