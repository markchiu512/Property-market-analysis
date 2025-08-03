import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_cleaning import *
from analysis import *

def main():
    print(" PROPERTY MARKET ANALYSIS ")
    print("=" * 60)
    
    df = load_data()
    most_affordable_cities(df)
    highest_value_cities(df)
    city_inventory_analysis(df)

if __name__ == "__main__":
    main()