import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_cleaning import load_data
from data_filters import filter_london_properties, get_london_property_stats
from visualizations import plot_london_price_by_property_type, plot_london_postcode_prices
from analysis import *


def main():
    print(" LONDON PROPERTY MARKET ANALYSIS ")
    print("=" * 60)
    
    # Check command line argument for dataset selection
    dataset = 'auto'
    if len(sys.argv) > 1:
        dataset = sys.argv[1]
        if dataset not in ['synthetic', 'real', 'sample', 'auto']:
            print(" Invalid dataset. Use: synthetic, real, sample, or auto")
            return
    
    try:
        # Load data and filter to London only
        df = load_data(dataset)
        london_df = filter_london_properties(df)
        
        if len(london_df) == 0:
            print("No London properties found in the dataset!")
            return
        
        print()
        print("=== LONDON PROPERTY STATISTICS ===")
        
        # Get London-specific statistics
        stats = get_london_property_stats(london_df)
        print(f"Total London properties: {stats['total_properties']:,}")
        print(f"Average price: £{stats['avg_price']:,.0f}")
        print(f"Median price: £{stats['median_price']:,.0f}")
        print(f"Price range: £{stats['min_price']:,.0f} - £{stats['max_price']:,.0f}")
        print(f"Number of postcode areas: {stats['postcode_areas']}")
        
        print("\n=== AVERAGE PRICES BY PROPERTY TYPE ===")
        for prop_type, avg_price in stats['avg_price_by_type'].items():
            type_names = {'D': 'Detached', 'S': 'Semi-detached', 'F': 'Flat/Apartment', 'T': 'Terraced', 'O': 'Other'}
            type_name = type_names.get(prop_type, prop_type)
            print(f"{type_name}: £{avg_price:,.0f}")
        
        print("\n=== LONDON AREA ANALYSIS ===")
        # Run standard analysis functions on London data
        most_affordable_cities(london_df)
        highest_value_cities(london_df)
        city_inventory_analysis(london_df)
        
        print("\n=== GENERATING LONDON-SPECIFIC CHARTS ===")
        # Generate London-specific visualizations
        plot_london_price_by_property_type(london_df)
        plot_london_postcode_prices(london_df)
        
        print("\nLondon analysis complete! Check outputs/charts/ for visualizations.")
        
    except FileNotFoundError as e:
        print(f" Error: {e}")
        print(" Use the helper scripts:")
        print("   ./scripts/use_synthetic.sh  # Generate synthetic data")
        print("   ./scripts/use_real.sh       # Process real data")
        print("   ./scripts/use_sample.sh     # Use real data sample")


if __name__ == "__main__":
    main()