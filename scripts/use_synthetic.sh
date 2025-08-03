#!/bin/bash
# Switch to using synthetic data for analysis

cd "$(dirname "$0")/.."

echo " Switching to synthetic data..."

# Generate synthetic data if it doesn't exist
if [ ! -f "data/processed/property_data_synthetic.csv" ]; then
    echo " Generating synthetic data..."
    source .venv/bin/activate
    python src/data_generator.py
fi

echo " Ready to analyze synthetic data (1,000 properties)"
echo " Run: cd scripts && python run_analysis.py"