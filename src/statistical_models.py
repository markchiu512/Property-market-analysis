import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima.model import ARIMA


def fit_sarima_model(ts, order=(1, 1, 1), seasonal_order=None):
    """
    Fit a SARIMA model to the time series data.
    
    Args:
        ts: Time series data
        order: (p, d, q) order of the ARIMA model
        seasonal_order: (P, D, Q, s) seasonal order of the ARIMA model
        
    Returns:
        Fitted SARIMA model result
    """
    
    # Auto-determine seasonal order if not provided
    if seasonal_order is None:
        if len(ts) > 100:  # Weekly data
            seasonal_order = (0, 1, 1, 52)
        else:  # Monthly data
            seasonal_order = (0, 1, 1, 12)
    
    print(f"\nFitting SARIMA{order} x {seasonal_order} model...")
    
    model = SARIMAX(ts, order=order, seasonal_order=seasonal_order,
                    enforce_stationarity=False, enforce_invertibility=False)
    sarima_result = model.fit(disp=False)
    
    print(f"Model fitted successfully!")
    print(f"AIC: {sarima_result.aic:.2f}")
    print(f"BIC: {sarima_result.bic:.2f}")
    
    return sarima_result


def fit_arima_model(ts, order=(1, 1, 1)):
    """
    Fit a simple ARIMA model (no seasonal component)
    
    Args:
        ts: Time series data
        order: (p, d, q) order of the ARIMA model
        
    Returns:
        Fitted ARIMA model result
    """
    print(f"\nFitting ARIMA{order} model...")
    
    model = ARIMA(ts, order=order)
    arima_result = model.fit()
    
    print(f"Model fitted successfully!")
    print(f"AIC: {arima_result.aic:.2f}")
    print(f"BIC: {arima_result.bic:.2f}")
    
    return arima_result


def compare_models(ts, model_configs):
    """
    Compare multiple SARIMA model configurations
    
    Args:
        ts: Time series data
        model_configs: List of tuples (order, seasonal_order)
        
    Returns:
        dict: Results with model configurations and their AIC/BIC scores
    """
    results = []
    
    print(f"\nComparing {len(model_configs)} model configurations...")
    print("-" * 70)
    
    for i, (order, seasonal_order) in enumerate(model_configs, 1):
        try:
            print(f"Model {i}: SARIMA{order} x {seasonal_order}")
            model_result = fit_sarima_model(ts, order=order, seasonal_order=seasonal_order)
            
            results.append({
                'order': order,
                'seasonal_order': seasonal_order,
                'model': model_result,
                'aic': model_result.aic,
                'bic': model_result.bic,
                'success': True
            })
            
            print(f"  Status: Success")
            
        except Exception as e:
            print(f"  Status: Failed ({str(e)[:50]}...)")
            results.append({
                'order': order,
                'seasonal_order': seasonal_order,
                'model': None,
                'aic': float('inf'),
                'bic': float('inf'),
                'success': False,
                'error': str(e)
            })
        
        print("-" * 70)
    
    # Find best model by AIC
    successful_results = [r for r in results if r['success']]
    if successful_results:
        best_result = min(successful_results, key=lambda x: x['aic'])
        print(f"\nBest model by AIC: SARIMA{best_result['order']} x {best_result['seasonal_order']}")
        print(f"AIC: {best_result['aic']:.2f}, BIC: {best_result['bic']:.2f}")
    else:
        best_result = None
        print("No models fitted successfully")
    
    return {
        'results': results,
        'best_model': best_result
    }


def forecast_2025(model_result, steps=None, ts_index=None):
    """
    Generate forecasts for 2025
    
    Args:
        model_result: Fitted SARIMA model result
        steps: Number of periods to forecast (auto-determined if None)
        ts_index: Original time series index for date continuation
        
    Returns:
        tuple: (forecast, confidence_intervals)
    """
    
    # Auto-determine forecast steps if not provided
    if steps is None:
        if ts_index is not None and len(ts_index) > 100:  # Weekly data
            steps = 52  # Forecast 52 weeks (1 year)
        else:  # Monthly data
            steps = 12  # Forecast 12 months (1 year)
    
    print(f"\nGenerating {steps}-period forecast...")
    
    # Get forecast
    forecast = model_result.forecast(steps=steps)
    forecast_ci = model_result.get_forecast(steps=steps).conf_int()
    
    # Create date index for forecast
    if ts_index is not None:
        last_date = ts_index[-1]
        
        # Determine frequency based on data
        if len(ts_index) > 100:  # Weekly data
            forecast_dates = pd.date_range(start=last_date + pd.DateOffset(weeks=1), 
                                         periods=steps, freq='W')
        else:  # Monthly data
            forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), 
                                         periods=steps, freq='ME')
        
        forecast.index = forecast_dates
        forecast_ci.index = forecast_dates
    
    return forecast, forecast_ci


def forecast_with_confidence(model_result, steps=None, ts_index=None, confidence_level=0.95):
    """
    Generate forecasts with custom confidence intervals
    
    Args:
        model_result: Fitted SARIMA model result  
        steps: Number of periods to forecast
        ts_index: Original time series index for date continuation
        confidence_level: Confidence level for intervals (e.g., 0.95 for 95%)
        
    Returns:
        dict: Forecast results with point forecasts and confidence intervals
    """
    
    if steps is None:
        if ts_index is not None and len(ts_index) > 100:
            steps = 52
        else:
            steps = 12
    
    print(f"\nGenerating {steps}-period forecast with {confidence_level*100}% confidence intervals...")
    
    # Get forecast with confidence intervals
    forecast_result = model_result.get_forecast(steps=steps)
    forecast = forecast_result.predicted_mean
    forecast_ci = forecast_result.conf_int(alpha=1-confidence_level)
    
    # Create date index for forecast
    if ts_index is not None:
        last_date = ts_index[-1]
        
        if len(ts_index) > 100:  # Weekly data
            forecast_dates = pd.date_range(start=last_date + pd.DateOffset(weeks=1), 
                                         periods=steps, freq='W')
        else:  # Monthly data  
            forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), 
                                         periods=steps, freq='ME')
        
        forecast.index = forecast_dates
        forecast_ci.index = forecast_dates
    
    return {
        'forecast': forecast,
        'confidence_intervals': forecast_ci, 
        'confidence_level': confidence_level,
        'forecast_result': forecast_result
    }


def model_diagnostics(model_result):
    """
    Print comprehensive model diagnostics
    
    Args:
        model_result: Fitted SARIMA model result
    """
    print(f"\n{'='*50}")
    print("MODEL DIAGNOSTICS")
    print(f"{'='*50}")
    
    print(f"Model: {model_result.model}")
    print(f"AIC: {model_result.aic:.2f}")
    print(f"BIC: {model_result.bic:.2f}")
    print(f"Log-Likelihood: {model_result.llf:.2f}")
    
    print(f"\nModel Parameters:")
    print(model_result.summary().tables[1])
    
    # Residual statistics
    residuals = model_result.resid
    print(f"\nResidual Statistics:")
    print(f"  Mean: {residuals.mean():.6f}")
    print(f"  Std Dev: {residuals.std():.6f}")
    print(f"  Min: {residuals.min():.2f}")
    print(f"  Max: {residuals.max():.2f}")
    
    return {
        'aic': model_result.aic,
        'bic': model_result.bic,
        'llf': model_result.llf,
        'residuals': residuals,
        'summary': model_result.summary()
    }


def compare_sales_volume_sarima_models(ts, model_configs, title="Sales Volume SARIMA Comparison"):
    """
    Compare multiple SARIMA models for sales volume and create comparison plot
    
    Args:
        ts: Sales volume time series data
        model_configs: List of tuples (order, seasonal_order, label)
        title: Title for analysis
        
    Returns:
        dict: Results with best model and comparison plot
    """
    import matplotlib.pyplot as plt
    import matplotlib
    import os
    
    results = []
    
    print(f"\n{'='*70}")
    print(f"SALES VOLUME SARIMA MODEL COMPARISON - {title.upper()}")
    print(f"{'='*70}")
    print(f"Testing {len(model_configs)} model configurations on {len(ts)} data points...")
    
    # Fit all models
    for i, (order, seasonal_order, label) in enumerate(model_configs, 1):
        try:
            print(f"\nModel {i}: {label} - SARIMA{order} x {seasonal_order}")
            model_result = fit_sarima_model(ts, order=order, seasonal_order=seasonal_order)
            
            # Generate forecast for plotting
            forecast_steps = min(26, len(ts) // 6)  # Forecast 26 periods ahead
            forecast, forecast_ci = forecast_2025(model_result, steps=forecast_steps, ts_index=ts.index)
            
            results.append({
                'label': label,
                'order': order,
                'seasonal_order': seasonal_order,
                'model': model_result,
                'forecast': forecast,
                'forecast_ci': forecast_ci,
                'aic': model_result.aic,
                'bic': model_result.bic,
                'success': True
            })
            
            print(f"  ✓ Success - AIC: {model_result.aic:.2f}, BIC: {model_result.bic:.2f}")
            
        except Exception as e:
            print(f"  ✗ Failed - {str(e)[:60]}...")
            results.append({
                'label': label,
                'order': order,
                'seasonal_order': seasonal_order,
                'model': None,
                'forecast': None,
                'forecast_ci': None,
                'aic': float('inf'),
                'bic': float('inf'),
                'success': False,
                'error': str(e)
            })
    
    # Find best model
    successful_results = [r for r in results if r['success']]
    if successful_results:
        best_result = min(successful_results, key=lambda x: x['aic'])
        print(f"\n🏆 BEST MODEL: {best_result['label']}")
        print(f"   SARIMA{best_result['order']} x {best_result['seasonal_order']}")
        print(f"   AIC: {best_result['aic']:.2f}, BIC: {best_result['bic']:.2f}")
    else:
        best_result = None
        print("\n❌ No models fitted successfully")
    
    # Create comparison plot
    print(f"\n📊 Creating model comparison plot...")
    _plot_sarima_model_comparison(ts, results, title)
    
    # Print summary table
    _print_model_comparison_table(results)
    
    return {
        'results': results,
        'best_model': best_result,
        'successful_count': len(successful_results)
    }


def _plot_sarima_model_comparison(ts, results, title):
    """Create comparison plot of SARIMA models"""
    import matplotlib.pyplot as plt
    import matplotlib
    import os
    
    # Setup plot
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'Sales Volume SARIMA Model Comparison - {title}', fontsize=16)
    
    # Colors for different models
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    successful_results = [r for r in results if r['success']]
    
    if not successful_results:
        # Show error message if no models worked
        for ax in axes.flat:
            ax.text(0.5, 0.5, 'No models fitted successfully', 
                   transform=ax.transAxes, ha='center', va='center', fontsize=12)
        return
    
    # Plot 1: Original time series with all forecasts
    axes[0, 0].plot(ts.index, ts.values, 'k-', linewidth=2, label='Actual', alpha=0.8)
    
    for i, result in enumerate(successful_results[:4]):  # Max 4 models to avoid clutter
        if result['forecast'] is not None:
            color = colors[i % len(colors)]
            axes[0, 0].plot(result['forecast'].index, result['forecast'].values, 
                           color=color, linestyle='--', linewidth=2, 
                           label=f"{result['label']} Forecast")
    
    axes[0, 0].set_title('Time Series with Forecasts')
    axes[0, 0].set_ylabel('Transaction Count')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: AIC Comparison
    labels = [r['label'] for r in successful_results]
    aic_values = [r['aic'] for r in successful_results]
    bars = axes[0, 1].bar(labels, aic_values, color=colors[:len(successful_results)])
    axes[0, 1].set_title('AIC Comparison (Lower is Better)')
    axes[0, 1].set_ylabel('AIC')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, value in zip(bars, aic_values):
        axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(aic_values)*0.01,
                       f'{value:.1f}', ha='center', va='bottom')
    
    # Plot 3: Residuals of best model
    if successful_results:
        best_model = min(successful_results, key=lambda x: x['aic'])
        residuals = best_model['model'].resid
        axes[1, 0].plot(residuals.index, residuals.values, 'g-', alpha=0.7)
        axes[1, 0].axhline(y=0, color='red', linestyle='--', alpha=0.5)
        axes[1, 0].set_title(f'Residuals - {best_model["label"]} (Best Model)')
        axes[1, 0].set_ylabel('Residuals')
        axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Forecast comparison (focus on forecasted period)
    if successful_results:
        for i, result in enumerate(successful_results):
            if result['forecast'] is not None:
                color = colors[i % len(colors)]
                axes[1, 1].plot(result['forecast'].index, result['forecast'].values, 
                               color=color, linewidth=2, marker='o', markersize=4,
                               label=f"{result['label']}")
                
                # Add confidence intervals for best model
                if result == min(successful_results, key=lambda x: x['aic']):
                    axes[1, 1].fill_between(result['forecast'].index,
                                           result['forecast_ci'].iloc[:, 0],
                                           result['forecast_ci'].iloc[:, 1],
                                           color=color, alpha=0.2)
        
        axes[1, 1].set_title('Forecast Comparison')
        axes[1, 1].set_ylabel('Predicted Transaction Count')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    charts_dir = os.path.join(project_root, 'outputs', 'charts')
    os.makedirs(charts_dir, exist_ok=True)
    
    chart_path = os.path.join(charts_dir, f'sarima_model_comparison_{title.lower().replace(" ", "_")}.png')
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    print(f"Model comparison plot saved to: {chart_path}")
    
    if matplotlib.get_backend() != 'Agg':
        plt.show()
    plt.close()


def _print_model_comparison_table(results):
    """Print formatted comparison table"""
    print(f"\n{'='*80}")
    print("MODEL COMPARISON SUMMARY")
    print(f"{'='*80}")
    print(f"{'Model':<25} {'Status':<10} {'AIC':<10} {'BIC':<10} {'Parameters':<25}")
    print(f"{'-'*80}")
    
    for result in results:
        if result['success']:
            status = "✓ Success"
            aic = f"{result['aic']:.1f}"
            bic = f"{result['bic']:.1f}"
        else:
            status = "✗ Failed"
            aic = "N/A"
            bic = "N/A"
        
        params = f"{result['order']} x {result['seasonal_order']}"
        print(f"{result['label']:<25} {status:<10} {aic:<10} {bic:<10} {params:<25}")
    
    print(f"{'-'*80}")