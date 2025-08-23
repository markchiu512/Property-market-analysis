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