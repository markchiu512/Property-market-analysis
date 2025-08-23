import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from time_series_analysis import (
    load_multi_year_data, 
    prepare_london_time_series
)
from statistical_models import (
    fit_sarima_model,
    forecast_2025,
    compare_models
)
import matplotlib
matplotlib.use('Agg')


def main():
    print(" SARIMA MODEL FITTING AND FORECASTING ")
    print("=" * 50)
    
    try:
        # Load data
        print("Loading data...")
        df = load_multi_year_data()
        london_ts = prepare_london_time_series(df, freq='W')
        
        print(f"\nLondon property time series:")
        print(f"  Data points: {len(london_ts)}")
        print(f"  Period: {london_ts.index[0].strftime('%Y-%m')} to {london_ts.index[-1].strftime('%Y-%m')}")
        print(f"  Average price: £{london_ts.mean():,.0f}")
        
        # Based on ACF/PACF analysis, try different parameter combinations
        # These are examples for weekly data - you should choose based on the ACF/PACF plots
        models_to_try = [
            ((1, 1, 1), (0, 1, 1, 52)),  # Basic SARIMA with 52-week seasonality
            ((1, 1, 0), (0, 1, 1, 52)),  # AR only
            ((0, 1, 1), (0, 1, 1, 52)),  # MA only
            ((2, 1, 2), (1, 1, 1, 52)),  # More complex
            ((1, 1, 1), (1, 1, 0, 52)),  # Seasonal AR only
        ]
        
        # Use the compare_models function for cleaner comparison
        comparison_result = compare_models(london_ts, models_to_try)
        best_model_info = comparison_result['best_model']
        
        if best_model_info is not None:
            best_model = best_model_info['model']
            best_params = (best_model_info['order'], best_model_info['seasonal_order'])
            print(f"\nBest model: SARIMA{best_params[0]} x {best_params[1]}")
            print(f"AIC: {best_model.aic:.2f}")
            print(f"BIC: {best_model.bic:.2f}")
            
            # Generate 2025 forecast
            print(f"\nGenerating 52-week forecast for 2025...")
            forecast, forecast_ci = forecast_2025(best_model, steps=52, ts_index=london_ts.index)
            
            print(f"\n2025 FORECAST SUMMARY (First 10 weeks):")
            print(f"{'Week':<12} {'Forecast (£)':<15} {'95% CI Lower':<15} {'95% CI Upper':<15}")
            print("-" * 65)
            
            # Show first 10 weeks to avoid too much output
            for i, (date, pred) in enumerate(forecast.head(10).items()):
                lower = forecast_ci.iloc[i, 0]
                upper = forecast_ci.iloc[i, 1]
                print(f"{date.strftime('%Y-W%U'):<12} £{pred:,.0f}      £{lower:,.0f}      £{upper:,.0f}")
            
            if len(forecast) > 10:
                print(f"... (showing first 10 of {len(forecast)} weeks)")
            
            # Summary statistics
            avg_forecast = forecast.mean()
            current_avg = london_ts.tail(26).mean()  # Last 26 weeks (6 months)
            change = (avg_forecast - current_avg) / current_avg * 100
            
            print(f"\nFORECAST ANALYSIS:")
            print(f"  Average 2025 forecast: £{avg_forecast:,.0f}")
            print(f"  Recent average (last 6 months): £{current_avg:,.0f}")
            print(f"  Projected change: {change:+.1f}%")
            
            print(f"\nForecasting complete!")
            
        else:
            print("No models successfully fitted. Try different parameter combinations.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()