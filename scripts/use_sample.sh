#!/bin/bash
# Switch to using real data sample for analysis

cd "$(dirname "$0")/.."

echo " Switching to real data sample..."

# Check if sample exists
if [ ! -f "data/samples/property_data_real_sample.csv" ]; then
    echo " Error: Real data sample not found"
    echo " Run ./scripts/use_real.sh first to create the sample"
    exit 1
fi

echo " Ready to analyze real data sample (5,000 properties)"
echo " Run: cd scripts && python run_analysis.py sample"