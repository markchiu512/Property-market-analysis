import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from time_series_analysis import (
    load_multi_year_data, 
    prepare_london_time_series,
    analyze_sarima_parameters
)
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend


def main():
    print(" SARIMA ANALYSIS - LONDON PROPERTY FORECASTING ")
    print("=" * 70)
    
    try:
        # Step 1: Load multi-year data
        print("\n1. Loading multi-year property data (2022-2024)...")
        df = load_multi_year_data()
        
        # Step 2: Prepare London time series
        print("\n2. Preparing London time series data...")
        london_ts = prepare_london_time_series(df, freq='W')
        
        print(f"Time series summary:")
        print(f"  Period: {london_ts.index[0].strftime('%Y-%m')} to {london_ts.index[-1].strftime('%Y-%m')}")
        print(f"  Data points: {len(london_ts)}")
        print(f"  Average price: £{london_ts.mean():,.0f}")
        print(f"  Price range: £{london_ts.min():,.0f} - £{london_ts.max():,.0f}")
        
        # Step 3: Analyze SARIMA parameters
        print("\n3. Analyzing SARIMA parameters...")
        recommendations = analyze_sarima_parameters(london_ts, "London Properties")
        
        # Step 4: Display recommendations
        print(f"\n4. Parameter recommendations:")
        print(f"   d (differencing): {recommendations['d']}")
        print(f"   D (seasonal differencing): {recommendations['D']}")
        print(f"   s (seasonal period): {recommendations['s']}")
        print(f"   Suggested p range: {recommendations['suggested_ranges']['p']}")
        print(f"   Suggested q range: {recommendations['suggested_ranges']['q']}")
        print(f"   Suggested P range: {recommendations['suggested_ranges']['P']}")
        print(f"   Suggested Q range: {recommendations['suggested_ranges']['Q']}")
        
        print(f"\n5. Next steps:")
        print(f"   - Review the ACF/PACF plots in outputs/charts/")
        print(f"   - Use the plots to determine optimal p, q, P, Q values")
        print(f"   - Fit SARIMA model with chosen parameters")
        print(f"   - Generate 2025 forecasts")
        
        print(f"\nAnalysis complete! Check outputs/charts/ for ACF/PACF and decomposition plots.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()