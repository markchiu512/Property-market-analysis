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
    diff_lags = min(lags, len(ts_diff) // 4)  # More conservative lag count
    
    # Debug info
    print(f"   Using {diff_lags} lags for {len(ts_diff)} data points")
    print(f"   Differenced series std: {ts_diff.std():.2f}")
    print(f"   Differenced series range: {ts_diff.min():.0f} to {ts_diff.max():.0f}")
    
    # ACF plot
    plot_acf(ts_diff, lags=diff_lags, ax=axes[1, 0], title='Autocorrelation Function (ACF)')
    
    # PACF plot  
    plot_pacf(ts_diff, lags=diff_lags, ax=axes[1, 1], title='Partial Autocorrelation Function (PACF)')
    
    plt.tight_layout()
    
    # Save the plot
    chart_path = os.path.join(charts_dir, f'acf_pacf_price_analysis_{title.lower().replace(" ", "_")}.png')
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    print(f"Price ACF/PACF analysis saved to: {chart_path}")
    
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


def prepare_london_sales_volume_time_series(df, freq='M'):
    """
    Prepare London sales volume (transaction count) as time series
    
    Args:
        df: Combined property dataframe
        freq: Frequency for time series ('M' for monthly, 'W' for weekly)
    
    Returns:
        pd.Series: Time series of London transaction counts
    """
    from data_filters import filter_london_properties
    
    # Filter to London properties
    london_df = filter_london_properties(df)
    
    # Ensure Date column is datetime
    london_df['Date'] = pd.to_datetime(london_df['Date'])
    
    # Set date as index and count transactions
    london_df = london_df.set_index('Date')
    
    # Resample by frequency and count transactions
    if freq == 'M':
        ts = london_df.resample('ME').size()  # Count transactions per month
        print(f"Created monthly sales volume time series with {len(ts)} data points")
    elif freq == 'W':
        ts = london_df.resample('W').size()  # Count transactions per week
        print(f"Created weekly sales volume time series with {len(ts)} data points")
    else:
        raise ValueError("Frequency must be 'M' (monthly) or 'W' (weekly)")
    
    # Fill any missing periods with 0 (no transactions)
    ts = ts.fillna(0)
    
    return ts


def plot_sales_volume_acf_pacf(ts, lags=None, title="Sales Volume"):
    """
    Plot ACF and PACF for sales volume time series
    
    Args:
        ts: Sales volume time series data
        lags: Number of lags to include
        title: Title for the plots
    """
    # Determine appropriate number of lags - use 52 for weekly data
    if lags is None:
        if len(ts) > 100:  # Weekly data
            lags = min(52, len(ts) // 3)  # Up to 52 weeks for annual patterns
        else:
            lags = min(24, len(ts) // 3)
    
    # Get the absolute path for saving
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    charts_dir = os.path.join(project_root, 'outputs', 'charts')
    os.makedirs(charts_dir, exist_ok=True)
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'Sales Volume ACF and PACF Analysis - {title}', fontsize=16)
    
    # Original time series
    axes[0, 0].plot(ts.index, ts.values)
    axes[0, 0].set_title('Original Sales Volume Series')
    axes[0, 0].set_ylabel('Transaction Count')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # First difference for stationarity
    ts_diff = ts.diff().dropna()
    axes[0, 1].plot(ts_diff.index, ts_diff.values)
    axes[0, 1].set_title('First Difference')
    axes[0, 1].set_ylabel('Change in Transaction Count')
    axes[0, 1].tick_params(axis='x', rotation=45)
    axes[0, 1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
    
    # Adjust lags for differenced series
    diff_lags = min(lags, len(ts_diff) // 4)
    
    # Debug info
    print(f"   Using {diff_lags} lags for {len(ts_diff)} data points")
    print(f"   Sales volume std: {ts.std():.2f}")
    print(f"   Sales volume range: {ts.min():.0f} to {ts.max():.0f} transactions")
    print(f"   Differenced series std: {ts_diff.std():.2f}")
    
    # ACF plot
    plot_acf(ts_diff, lags=diff_lags, ax=axes[1, 0], title='Autocorrelation Function (ACF)')
    
    # PACF plot  
    plot_pacf(ts_diff, lags=diff_lags, ax=axes[1, 1], title='Partial Autocorrelation Function (PACF)')
    
    plt.tight_layout()
    
    # Save the plot
    chart_path = os.path.join(charts_dir, f'acf_pacf_sales_volume_weekly_{title.lower().replace(" ", "_")}.png')
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    print(f"Weekly sales volume ACF/PACF analysis saved to: {chart_path}")
    
    # Only show if running in interactive mode
    if matplotlib.get_backend() != 'Agg':
        plt.show()
    plt.close()
    
    return ts_diff


def analyze_sales_volume_sarima_parameters(df, title="London Sales Volume"):
    """
    Analyze sales volume time series to determine SARIMA parameters
    
    Args:
        df: Combined property dataframe
        title: Title for analysis
        
    Returns:
        dict: Recommended parameters and analysis results
    """
    print(f"\n{'='*60}")
    print(f"SALES VOLUME SARIMA ANALYSIS - {title.upper()}")
    print(f"{'='*60}")
    
    # Prepare weekly sales volume time series (to match price analysis)
    ts = prepare_london_sales_volume_time_series(df, freq='W')
    
    print(f"Sales volume summary:")
    print(f"  Period: {ts.index[0].strftime('%Y-%m')} to {ts.index[-1].strftime('%Y-%m')}")
    print(f"  Data points: {len(ts)}")
    print(f"  Average weekly transactions: {ts.mean():.1f}")
    print(f"  Peak week: {ts.max():.0f} transactions")
    print(f"  Low week: {ts.min():.0f} transactions")
    
    # 1. Check stationarity of original series
    is_stationary = check_stationarity(ts, "Original Sales Volume")
    
    # 2. Check stationarity of first difference
    ts_diff = ts.diff().dropna()
    is_diff_stationary = check_stationarity(ts_diff, "First Difference Sales Volume")
    
    # 3. Generate ACF/PACF plots
    print(f"\nGenerating sales volume ACF/PACF plots...")
    ts_diff = plot_sales_volume_acf_pacf(ts, title=title)
    
    # 4. Parameter recommendations for sales volume
    print(f"\n{'='*50}")
    print("SALES VOLUME SARIMA PARAMETER RECOMMENDATIONS:")
    print(f"{'='*50}")
    
    # Determine d (differencing order)
    d_param = 1 if not is_stationary and is_diff_stationary else 0
    
    print(f"Based on sales volume characteristics:")
    print(f"  d (differencing order): {d_param}")
    print(f"  D (seasonal differencing): 1 (for weekly seasonality)")
    print(f"  s (seasonal period): 52 (weekly data)")
    
    print(f"\nSales volume with weekly data:")
    print(f"  - Look for significant spikes at lags 13, 26, 52 (quarterly/annual patterns)")
    print(f"  - Weekly count data may show different patterns than monthly")
    print(f"  - 52-week seasonality captures annual buying cycles")
    
    recommendations = {
        'd': d_param,
        'D': 1,
        's': 52,
        'frequency': 'weekly',
        'data_type': 'sales_volume',
        'suggested_ranges': {
            'p': [0, 1, 2],
            'q': [0, 1, 2], 
            'P': [0, 1, 2],  # May need stronger seasonal AR
            'Q': [0, 1, 2]   # May need stronger seasonal MA
        }
    }
    
    return recommendations


def analyze_sales_volume_sarima_parameters_monthly(df, title="London Sales Volume Monthly"):
    """
    Analyze monthly sales volume time series to determine SARIMA parameters (36 data points)
    
    Args:
        df: Combined property dataframe
        title: Title for analysis
        
    Returns:
        dict: Recommended parameters and analysis results
    """
    print(f"\n{'='*60}")
    print(f"MONTHLY SALES VOLUME SARIMA ANALYSIS - {title.upper()}")
    print(f"{'='*60}")
    
    # Prepare monthly sales volume time series
    ts = prepare_london_sales_volume_time_series(df, freq='M')
    
    print(f"Monthly sales volume summary:")
    print(f"  Period: {ts.index[0].strftime('%Y-%m')} to {ts.index[-1].strftime('%Y-%m')}")
    print(f"  Data points: {len(ts)}")
    print(f"  Average monthly transactions: {ts.mean():.1f}")
    print(f"  Peak month: {ts.max():.0f} transactions")
    print(f"  Low month: {ts.min():.0f} transactions")
    
    # 1. Check stationarity of original series
    is_stationary = check_stationarity(ts, "Original Monthly Sales Volume")
    
    # 2. Check stationarity of first difference
    ts_diff = ts.diff().dropna()
    is_diff_stationary = check_stationarity(ts_diff, "First Difference Monthly Sales Volume")
    
    # 3. Generate ACF/PACF plots with monthly-specific parameters
    print(f"\nGenerating monthly sales volume ACF/PACF plots...")
    ts_diff = plot_sales_volume_acf_pacf_monthly(ts, title=title)
    
    # 4. Parameter recommendations for monthly sales volume
    print(f"\n{'='*50}")
    print("MONTHLY SALES VOLUME SARIMA PARAMETER RECOMMENDATIONS:")
    print(f"{'='*50}")
    
    # Determine d (differencing order)
    d_param = 1 if not is_stationary and is_diff_stationary else 0
    
    print(f"Based on monthly sales volume characteristics:")
    print(f"  d (differencing order): {d_param}")
    print(f"  D (seasonal differencing): 1 (for monthly seasonality)")
    print(f"  s (seasonal period): 12 (monthly data)")
    
    print(f"\nMonthly sales volume analysis:")
    print(f"  - Look for significant spikes at lags 12, 24 (annual patterns)")
    print(f"  - Monthly aggregation smooths weekly variations")
    print(f"  - Clearer seasonal patterns than weekly data")
    
    recommendations = {
        'd': d_param,
        'D': 1,
        's': 12,
        'frequency': 'monthly',
        'data_type': 'sales_volume_monthly',
        'suggested_ranges': {
            'p': [0, 1, 2],
            'q': [0, 1, 2], 
            'P': [0, 1, 2],
            'Q': [0, 1, 2]
        }
    }
    
    return recommendations


def plot_sales_volume_acf_pacf_monthly(ts, lags=None, title="Monthly Sales Volume"):
    """
    Plot ACF and PACF for monthly sales volume time series
    
    Args:
        ts: Sales volume time series data (monthly)
        lags: Number of lags to include
        title: Title for the plots
    """
    # Determine appropriate number of lags for monthly data
    if lags is None:
        lags = min(24, len(ts) // 3)  # Up to 24 months for seasonal patterns
    
    # Get the absolute path for saving
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    charts_dir = os.path.join(project_root, 'outputs', 'charts')
    os.makedirs(charts_dir, exist_ok=True)
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'Monthly Sales Volume ACF and PACF Analysis - {title}', fontsize=16)
    
    # Original time series
    axes[0, 0].plot(ts.index, ts.values)
    axes[0, 0].set_title('Original Monthly Sales Volume Series')
    axes[0, 0].set_ylabel('Monthly Transaction Count')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # First difference for stationarity
    ts_diff = ts.diff().dropna()
    axes[0, 1].plot(ts_diff.index, ts_diff.values)
    axes[0, 1].set_title('First Difference')
    axes[0, 1].set_ylabel('Change in Monthly Transaction Count')
    axes[0, 1].tick_params(axis='x', rotation=45)
    axes[0, 1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
    
    # Adjust lags for differenced series
    diff_lags = min(lags, len(ts_diff) // 4)
    
    # Debug info
    print(f"   Using {diff_lags} lags for {len(ts_diff)} monthly data points")
    print(f"   Monthly sales volume std: {ts.std():.2f}")
    print(f"   Monthly sales volume range: {ts.min():.0f} to {ts.max():.0f} transactions")
    print(f"   Differenced series std: {ts_diff.std():.2f}")
    
    # ACF plot
    plot_acf(ts_diff, lags=diff_lags, ax=axes[1, 0], title='Autocorrelation Function (ACF)')
    
    # PACF plot  
    plot_pacf(ts_diff, lags=diff_lags, ax=axes[1, 1], title='Partial Autocorrelation Function (PACF)')
    
    plt.tight_layout()
    
    # Save the plot with different name
    chart_path = os.path.join(charts_dir, f'acf_pacf_sales_volume_monthly_{title.lower().replace(" ", "_")}.png')
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    print(f"Monthly sales volume ACF/PACF analysis saved to: {chart_path}")
    
    # Only show if running in interactive mode
    if matplotlib.get_backend() != 'Agg':
        plt.show()
    plt.close()
    
    return ts_diff