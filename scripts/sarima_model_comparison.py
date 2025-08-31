import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from time_series_analysis import load_multi_year_data, prepare_london_sales_volume_time_series
from statistical_models import compare_sales_volume_sarima_models
import matplotlib
matplotlib.use('Agg')


def main():
    print(" SARIMA MODEL COMPARISON - LONDON SALES VOLUME ")
    print("=" * 70)
    
    try:
        # Load 3-year data
        print("Loading multi-year property data (2022-2024)...")
        df = load_multi_year_data()
        
        # Run both weekly and monthly analyses for complete comparison (8 models total)
        frequencies = [
            ('W', 52, 'Weekly'),
            ('M', 12, 'Monthly')
        ]
        
        all_results = []
        
        for freq, seasonal_period, freq_name in frequencies:
            print(f"\n{'='*50}")
            print(f"ANALYZING {freq_name.upper()} DATA")
            print(f"{'='*50}")
            
            print(f"\nPreparing {freq_name.upper()} sales volume time series...")
            ts = prepare_london_sales_volume_time_series(df, freq=freq)
            
            # Define 4 model configurations for this frequency
            model_configs = [
                ((1, 1, 1), (0, 1, 1, seasonal_period), f"Basic SARIMA ({freq_name})"),
                ((0, 1, 1), (0, 1, 1, seasonal_period), f"Pure MA ({freq_name})"),
                ((1, 1, 0), (1, 1, 0, seasonal_period), f"AR with Seasonal ({freq_name})"),
                ((2, 1, 2), (1, 1, 1, seasonal_period), f"Complex Model ({freq_name})")
            ]
            
            print(f"Time series prepared:")
            print(f"  Period: {ts.index[0].strftime('%Y-%m')} to {ts.index[-1].strftime('%Y-%m')}")
            print(f"  Data points: {len(ts)}")
            print(f"  Frequency: {freq} ({freq_name})")
            print(f"  Seasonal period: {seasonal_period}")
            print(f"  Average transactions per period: {ts.mean():.1f}")
            
            # Run model comparison for this frequency
            title = f"London_{freq_name}_Sales_Volume"
            results = compare_sales_volume_sarima_models(ts, model_configs, title=title)
            
            # Store results
            all_results.append({
                'frequency': freq_name,
                'results': results,
                'model_count': len(model_configs)
            })
            
            # Summary for this frequency
            if results['successful_count'] > 0:
                print(f"\n✅ {freq_name.upper()} ANALYSIS COMPLETE!")
                print(f"   Successfully fitted: {results['successful_count']}/{len(model_configs)} models")
                print(f"   Best {freq_name.lower()} model: {results['best_model']['label']}")
            else:
                print(f"\n❌ {freq_name.upper()} ANALYSIS FAILED!")
                print(f"   No {freq_name.lower()} models fitted successfully")
        
        # Overall summary
        print(f"\n{'='*70}")
        print("FINAL SUMMARY - ALL 8 SARIMA MODELS")
        print(f"{'='*70}")
        
        total_successful = sum(r['results']['successful_count'] for r in all_results)
        total_models = sum(r['model_count'] for r in all_results)
        
        print(f"Total models tested: {total_models}")
        print(f"Successfully fitted: {total_successful}")
        
        # Find overall best model
        best_models = []
        for freq_result in all_results:
            if freq_result['results']['successful_count'] > 0:
                best_model = freq_result['results']['best_model']
                best_models.append({
                    'frequency': freq_result['frequency'],
                    'label': best_model['label'],
                    'aic': best_model['aic']
                })
        
        if best_models:
            overall_best = min(best_models, key=lambda x: x['aic'])
            print(f"\nOverall best model: {overall_best['label']} (AIC: {overall_best['aic']:.2f})")
            print(f"Check outputs/charts/ for comparison plots")
        else:
            print(f"\n❌ No models fitted successfully across all frequencies")
            print(f"   Consider adjusting parameter combinations")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()