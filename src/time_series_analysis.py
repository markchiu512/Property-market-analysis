import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
import os
import matplotlib
from data_filters import filter_london_properties


def load_multi_year_data():
    """Load and combine property data from 2022-2024"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    all_data = []
    years = ['2022', '2023', '2024']
    
    for year in years:
        raw_path = os.path.join(project_root, 'data', 'raw', f'pp-{year}.csv')
        print(f"Loading {year} data...")
        
        if os.path.exists(raw_path):
            # Load and clean data similar to clean_pp_data function
            df = pd.read_csv(raw_path, header=None)
            df_clean = df[[1, 2, 3, 4, 5, 6, 11]].copy()
            df_clean.columns = ['Price', 'Date', 'Postcode', 'Property_Type', 
                               'New_built_indicator', 'Tenure_Type', 'City']
            
            # Clean date format
            df_clean['Date'] = df_clean['Date'].str.split(' ').str[0]
            df_clean['Date'] = pd.to_datetime(df_clean['Date'])
            
            # Create Postcode_Area
            df_clean['Postcode_Area'] = np.where(
                df_clean['Postcode'].str[1].str.isdigit(),
                df_clean['Postcode'].str[0],
                df_clean['Postcode'].str[:2])
            
            # Filter out unreasonably low prices
            df_clean = df_clean[df_clean['Price'] >= 30000]
            
            all_data.append(df_clean)
            print(f"Loaded {len(df_clean)} properties from {year}")
        else:
            print(f"Warning: {raw_path} not found")
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"Combined total: {len(combined_df)} properties from {len(all_data)} years")
        return combined_df
    else:
        raise FileNotFoundError("No raw data files found")


def prepare_london_time_series(df, freq='W'):
    """
    Prepare London property data as time series
    
    Args:
        df: Combined property dataframe
        freq: Frequency for time series ('W' for weekly, 'M' for monthly, 'Q' for quarterly)
    
    Returns:
        pd.Series: Time series of average weekly/monthly/quarterly London property prices
    """
    # Filter to London properties
    london_df = filter_london_properties(df)
    
    # Ensure Date column is datetime
    london_df['Date'] = pd.to_datetime(london_df['Date'])
    
    # Set date as index and resample
    london_df = london_df.set_index('Date')
    
    # Resample by frequency and calculate mean price
    if freq == 'W':
        ts = london_df['Price'].resample('W').mean()
        print(f"Created weekly time series with {len(ts)} data points")
    elif freq == 'M':
        ts = london_df['Price'].resample('ME').mean()
        print(f"Created monthly time series with {len(ts)} data points")
    elif freq == 'Q':
        ts = london_df['Price'].resample('QE').mean()
        print(f"Created quarterly time series with {len(ts)} data points")
    else:
        raise ValueError("Frequency must be 'W' (weekly), 'M' (monthly) or 'Q' (quarterly)")
    
    # Remove any NaN values
    ts = ts.dropna()
    
    return ts


def check_stationarity(ts, title="Time Series"):
    """
    Check stationarity using Augmented Dickey-Fuller test
    
    Args:
        ts: Time series data
        title: Title for the test
    """
    print(f"\n=== Stationarity Test for {title} ===")
    
    # Perform Augmented Dickey-Fuller test
    result = adfuller(ts)
    
    print(f'ADF Statistic: {result[0]:.6f}')
    print(f'p-value: {result[1]:.6f}')
    print('Critical Values:')
    for key, value in result[4].items():
        print(f'\t{key}: {value:.3f}')
    
    if result[1] <= 0.05:
        print("Result: Time series is stationary (reject null hypothesis)")
        return True
    else:
        print("Result: Time series is non-stationary (fail to reject null hypothesis)")
        return False


def plot_acf_pacf(ts, lags=None, title="Time Series"):
    """
    Plot ACF and PACF to help determine SARIMA parameters
    
    Args:
        ts: Time series data
        lags: Number of lags to include
        title: Title for the plots
    """
    # Determine appropriate number of lags
    # For weekly data: use up to 52 lags to capture annual seasonality
    # For other frequencies: use conservative approach
    if lags is None:
        if len(ts) > 100:  # Likely weekly data
            lags = min(52, len(ts) // 3)  # Up to 52 lags for annual patterns
        else:  # Monthly or quarterly data
            lags = min(20, len(ts) // 3)
    
    # Get the absolute path for saving
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    charts_dir = os.path.join(project_root, 'outputs', 'charts')
    os.makedirs(charts_dir, exist_ok=True)
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'ACF and PACF Analysis - {title}', fontsize=16)
    
    # Original time series
    axes[0, 0].plot(ts.index, ts.values)
    axes[0, 0].set_title('Original Time Series')
    axes[0, 0].set_ylabel('Average Price (£)')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # First difference (if needed for stationarity)
    ts_diff = ts.diff().dropna()
    axes[0, 1].plot(ts_diff.index, ts_diff.values)
    axes[0, 1].set_title('First Difference')
    axes[0, 1].set_ylabel('Price Difference (£)')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Adjust lags for differenced series (one less data point)
    diff_lags = min(lags, len(ts_diff) // 3)
    
    # ACF plot
    plot_acf(ts_diff, lags=diff_lags, ax=axes[1, 0], title='Autocorrelation Function (ACF)')
    
    # PACF plot
    plot_pacf(ts_diff, lags=diff_lags, ax=axes[1, 1], title='Partial Autocorrelation Function (PACF)')
    
    plt.tight_layout()
    
    # Save the plot
    chart_path = os.path.join(charts_dir, f'acf_pacf_analysis_{title.lower().replace(" ", "_")}.png')
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    print(f"ACF/PACF analysis saved to: {chart_path}")
    
    # Only show if running in interactive mode
    if matplotlib.get_backend() != 'Agg':
        plt.show()
    plt.close()
    
    return ts_diff


def plot_seasonal_decomposition(ts, title="Time Series"):
    """
    Plot seasonal decomposition
    
    Args:
        ts: Time series data
        title: Title for the plots
    """
    print(f"\nPerforming seasonal decomposition...")
    try:
        # Determine seasonal period based on data frequency
        if len(ts) > 100:  # Likely weekly data
            seasonal_period = 52  # 52 weeks = 1 year
        else:  # Monthly data
            seasonal_period = 12  # 12 months = 1 year
        
        decomposition = seasonal_decompose(ts, model='additive', period=seasonal_period)
        
        # Plot seasonal decomposition
        fig, axes = plt.subplots(4, 1, figsize=(15, 12))
        fig.suptitle(f'Seasonal Decomposition - {title}', fontsize=16)
        
        decomposition.observed.plot(ax=axes[0], title='Original')
        decomposition.trend.plot(ax=axes[1], title='Trend')
        decomposition.seasonal.plot(ax=axes[2], title='Seasonal')
        decomposition.resid.plot(ax=axes[3], title='Residual')
        
        plt.tight_layout()
        
        # Save decomposition plot
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        charts_dir = os.path.join(project_root, 'outputs', 'charts')
        chart_path = os.path.join(charts_dir, f'seasonal_decomposition_{title.lower().replace(" ", "_")}.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        print(f"Seasonal decomposition saved to: {chart_path}")
        
        if matplotlib.get_backend() != 'Agg':
            plt.show()
        plt.close()
        
        return decomposition
        
    except Exception as e:
        print(f"Seasonal decomposition failed: {e}")
        return None


def analyze_sarima_parameters(ts, title="London Properties"):
    """
    Comprehensive analysis to determine SARIMA parameters
    
    Args:
        ts: Time series data
        title: Title for analysis
        
    Returns:
        dict: Recommended parameters and analysis results
    """
    print(f"\n{'='*60}")
    print(f"SARIMA PARAMETER ANALYSIS - {title.upper()}")
    print(f"{'='*60}")
    
    # 1. Check stationarity of original series
    is_stationary = check_stationarity(ts, "Original Series")
    
    # 2. Check stationarity of first difference
    ts_diff = ts.diff().dropna()
    is_diff_stationary = check_stationarity(ts_diff, "First Difference")
    
    # 3. Generate ACF/PACF plots
    print(f"\nGenerating ACF/PACF plots...")
    ts_diff = plot_acf_pacf(ts, title=title)
    
    # 4. Seasonal decomposition
    decomposition = plot_seasonal_decomposition(ts, title=title)
    
    # 5. Parameter recommendations
    print(f"\n{'='*50}")
    print("SARIMA PARAMETER RECOMMENDATIONS:")
    print(f"{'='*50}")
    
    # Determine d (differencing order)
    d_param = 1 if not is_stationary and is_diff_stationary else 0
    
    # Determine seasonal period and provide appropriate guidance
    if len(ts) > 100:  # Weekly data
        seasonal_period = 52
        seasonal_lags = "52, 104 (for weekly data)"
        frequency_type = "weekly"
    else:  # Monthly data
        seasonal_period = 12
        seasonal_lags = "12, 24, 36 (for monthly data)"
        frequency_type = "monthly"
    
    print(f"Based on stationarity tests:")
    print(f"  d (differencing order): {d_param}")
    print(f"  D (seasonal differencing): 1 (recommended for seasonal data)")
    
    print(f"\nTo determine p, q, P, Q parameters for {frequency_type} data:")
    print(f"  1. Look at the ACF plot:")
    print(f"     - If ACF cuts off after lag q, suggests MA(q) component")
    print(f"     - If ACF decays slowly, suggests differencing needed")
    print(f"  2. Look at the PACF plot:")
    print(f"     - If PACF cuts off after lag p, suggests AR(p) component")
    print(f"  3. For seasonal components (P, Q):")
    print(f"     - Look at seasonal lags ({seasonal_lags})")
    print(f"     - Similar interpretation as p, q but at seasonal lags")
    
    if len(ts) > 100:  # Weekly data - focus on key lags
        print(f"  4. Key lags to examine for weekly data:")
        print(f"     - Lags 1-4: Short-term weekly effects")
        print(f"     - Lag 13: Quarterly effects (~3 months)")
        print(f"     - Lag 26: Semi-annual effects (~6 months)")
        print(f"     - Lag 52: Annual seasonal effects")
    
    recommendations = {
        'd': d_param,
        'D': 1,
        's': seasonal_period,
        'frequency': frequency_type,
        'suggested_ranges': {
            'p': [0, 1, 2],
            'q': [0, 1, 2], 
            'P': [0, 1],
            'Q': [0, 1]
        },
        'decomposition': decomposition
    }
    
    return recommendations