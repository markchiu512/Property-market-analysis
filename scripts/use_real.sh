#!/bin/bash
# Switch to using real data for analysis

cd "$(dirname "$0")/.."

echo " Switching to real data..."

# Check if raw data exists
if [ ! -f "data/raw/pp-2024.csv" ]; then
    echo " Error: pp-2024.csv not found in data/raw/"
    echo " Please download the real property data file first"
    exit 1
fi

# Process real data if not already done
if [ ! -f "data/processed/property_data_real.csv" ]; then
    echo " Processing real data (this may take several minutes)..."
    source .venv/bin/activate
    python -c "from src.data_cleaning import clean_pp_data; clean_pp_data()"
fi

echo " Ready to analyze real data (~820,000 properties)"
echo " Run: cd scripts && python run_analysis.py"
echo " Or use sample: python run_analysis.py sample"