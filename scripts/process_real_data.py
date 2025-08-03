#!/usr/bin/env python3
"""
Process raw pp-2024.csv data into cleaned format
"""
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_cleaning import clean_pp_data

def main():
    print(" PROPERTY DATA PROCESSOR")
    print("=" * 50)
    
    try:
        print(" Processing raw pp-2024.csv data...")
        print("  This may take several minutes for 820,000+ records")
        print()
        
        df = clean_pp_data()
        
        print()
        print(" Processing complete!")
        print(f" Processed {len(df)} property records")
        print(" Files created:")
        print("   - property_data_real.csv (full dataset)")
        print("   - property_data_real_sample.csv (5K sample)")
        print()
        print(" Ready to analyze! Run:")
        print("   cd scripts && python run_analysis.py real")
        
    except FileNotFoundError:
        print(" Error: pp-2024.csv not found in data/raw/")
        print(" Please download the raw property data file first")
        return 1
    except Exception as e:
        print(f" Error processing data: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())