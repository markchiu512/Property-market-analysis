import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def _calculate_city_average_prices(df):
    # Always group by Postcode_Area for consistent geographic analysis
    average_prices = df.groupby('Postcode_Area')['Price'].mean()
    return average_prices

def _get_city_for_postcode(df, postcode_area):
    """Get a representative city name for a given postcode area"""
    if 'City' in df.columns and 'Postcode_Area' in df.columns:
        # Get the most common city name for this postcode area
        city = df[df['Postcode_Area'] == postcode_area]['City'].mode()
        if len(city) > 0:
            return city.iloc[0]
    return None


def most_affordable_cities(df):
    cheapest_area_avg = _calculate_city_average_prices(df)
    cheapest_postcode = cheapest_area_avg.idxmin()
    cheapest_price = cheapest_area_avg[cheapest_postcode]
    
    # Get city name for display
    city_name = _get_city_for_postcode(df, cheapest_postcode)
    if city_name:
        print(f" Most affordable area: {city_name} ({cheapest_postcode}) £{cheapest_price:,.0f}")
    else:
        print(f" Most affordable area: {cheapest_postcode} £{cheapest_price:,.0f}")
    return 

def highest_value_cities(df):
    highest_area_avg = _calculate_city_average_prices(df)
    highest_postcode = highest_area_avg.idxmax()
    highest_price = highest_area_avg[highest_postcode]
    
    # Get city name for display
    city_name = _get_city_for_postcode(df, highest_postcode)
    if city_name:
        print(f" Highest value area: {city_name} ({highest_postcode}) £{highest_price:,.0f}")
    else:
        print(f" Highest value area: {highest_postcode} £{highest_price:,.0f}")
    return 

def city_inventory_analysis(df):
    # Always group by Postcode_Area for consistent analysis
    inventory_counts = df.groupby('Postcode_Area').size()
    location_type = "Area"
    
    most_inventory_postcode = inventory_counts.idxmax()
    most_inventory_count = inventory_counts.max()
    
    # Find all postcode areas with minimum count
    least_inventory_count = inventory_counts.min()
    least_inventory_postcodes = inventory_counts[inventory_counts == least_inventory_count].index.tolist()
    
    # Format display for most choices
    city_name = _get_city_for_postcode(df, most_inventory_postcode)
    if city_name:
        print(f"{location_type} with most choices: {city_name} ({most_inventory_postcode}) ({most_inventory_count} properties)")
    else:
        print(f"{location_type} with most choices: {most_inventory_postcode} ({most_inventory_count} properties)")
    
    # Format display for least choices
    if len(least_inventory_postcodes) == 1:
        city_name = _get_city_for_postcode(df, least_inventory_postcodes[0])
        if city_name:
            print(f"{location_type} with least choices: {city_name} ({least_inventory_postcodes[0]}) ({least_inventory_count} properties)")
        else:
            print(f"{location_type} with least choices: {least_inventory_postcodes[0]} ({least_inventory_count} properties)")
    else:
        # Show first few with city names
        formatted_areas = []
        for postcode in least_inventory_postcodes[:3]:  # Show first 3
            city_name = _get_city_for_postcode(df, postcode)
            if city_name:
                formatted_areas.append(f"{city_name} ({postcode})")
            else:
                formatted_areas.append(str(postcode))
        
        areas_str = ", ".join(formatted_areas)
        if len(least_inventory_postcodes) > 3:
            areas_str += f" and {len(least_inventory_postcodes) - 3} others"
        print(f"{location_type}s with least choices: {areas_str} ({least_inventory_count} properties each)")
    
    return 

def price_comparison_by_new_built_status(df):
    new_built_avg_prices = df[df['New_built_indicator'] == 'Y']['Price'].mean()
    existing_built_avg_prices = df[df['New_built_indicator'] == 'N']['Price'].mean()
    print(f"Average price of new builds: £{new_built_avg_prices:,.0f}")
    print(f"Average price of existing properties: £{existing_built_avg_prices:,.0f}")
    return

def price_comparison_by_tenure_type(df):
    freehold_avg_prices = df[df['Tenure_Type'] == 'F']['Price'].mean()
    leasehold_avg_prices = df[df['Tenure_Type'] == 'L']['Price'].mean()
    print(f"Average price of freehold properties: £{freehold_avg_prices:,.0f}")
    print(f"Average price of leasehold properties: £{leasehold_avg_prices:,.0f}")
    return