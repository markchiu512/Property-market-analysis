1. Starting the Script

  cd scripts
  python run_analysis.py

2. What Happens Inside:

  Step 1: Check Command Line Arguments
  - If you just run python run_analysis.py → uses "auto" mode
  - If you run python run_analysis.py real → uses real data
  - If you run python run_analysis.py synthetic → uses synthetic data
  - If you run python run_analysis.py sample → uses sample data

  Step 2: Load Data
  - Calls load_data(dataset) function from data_cleaning.py
  - This function looks for the right CSV file based on what you chose:
    - auto: Tries real data first, falls back to synthetic if not found
    - real: Looks for property_data_real.csv (820K records)
    - synthetic: Looks for property_data_synthetic.csv (1K records)
    - sample: Looks for property_data_real_sample.csv (5K records)

  Step 3: Run Analysis
  - Calls three analysis functions from analysis.py:
    - most_affordable_cities(df) → finds cheapest postcode
    - highest_value_cities(df) → finds most expensive postcode
    - city_inventory_analysis(df) → finds postcode with most/least properties


  Option A: Use Synthetic Data

  ./scripts/use_synthetic.sh   
  cd scripts
  python run_analysis.py      

  Option B: Use Real Data

  ./scripts/use_real.sh   
  cd scripts
  python run_analysis.py real  

  Option C: Use Sample

  ./scripts/use_real.sh        
  cd scripts
  python run_analysis.py sample # Analyzes 5K records instead of 820K
