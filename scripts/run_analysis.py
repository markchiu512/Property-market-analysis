import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_cleaning import load_data
from analysis import most_affordable_cities, highest_value_cities, city_inventory_analysis

def main():
    import sys
    
    print(" PROPERTY MARKET ANALYSIS ")
    print("=" * 60)
    
    # Check command line argument for dataset selection
    dataset = 'auto'
    if len(sys.argv) > 1:
        dataset = sys.argv[1]
        if dataset not in ['synthetic', 'real', 'sample', 'auto']:
            print(" Invalid dataset. Use: synthetic, real, sample, or auto")
            print(" Examples:")
            print("   python run_analysis.py           # Auto-detect")
            print("   python run_analysis.py synthetic # Use synthetic data")
            print("   python run_analysis.py real      # Use real data")
            print("   python run_analysis.py sample    # Use real data sample")
            return
    
    try:
        df = load_data(dataset)
        print()
        most_affordable_cities(df)
        highest_value_cities(df)
        city_inventory_analysis(df)
    except FileNotFoundError as e:
        print(f" Error: {e}")
        print(" Use the helper scripts:")
        print("   ./scripts/use_synthetic.sh  # Generate synthetic data")
        print("   ./scripts/use_real.sh       # Process real data")
        print("   ./scripts/use_sample.sh     # Use real data sample")

if __name__ == "__main__":
    main()