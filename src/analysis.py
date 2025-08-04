import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def _calculate_city_average_prices(df):
    # Use City column if available, otherwise fall back to Postcode_Area
    if 'City' in df.columns:
        average_prices = df.groupby('City')['Price'].mean()
    else:
        average_prices = df.groupby('Postcode_Area')['Price'].mean()
    return average_prices

def _get_postcode_for_city(df, city_name):
    """Get the postcode area for a given city name"""
    if 'City' in df.columns and 'Postcode_Area' in df.columns:
        postcode = df[df['City'] == city_name]['Postcode_Area'].iloc[0]
        return postcode
    return None


def most_affordable_cities(df):
    cheapest_city_avg = _calculate_city_average_prices(df)
    cheapest_city = cheapest_city_avg.idxmin()
    cheapest_price = cheapest_city_avg[cheapest_city]
    
    # Get postcode area for display
    postcode_area = _get_postcode_for_city(df, cheapest_city)
    if postcode_area:
        print(f" Most affordable area: {cheapest_city} ({postcode_area}) £{cheapest_price:,.0f}")
    else:
        print(f" Most affordable area: {cheapest_city} £{cheapest_price:,.0f}")
    return 

def highest_value_cities(df):
    highest_city_avg = _calculate_city_average_prices(df)
    highest_city = highest_city_avg.idxmax()
    highest_price = highest_city_avg[highest_city]
    
    # Get postcode area for display
    postcode_area = _get_postcode_for_city(df, highest_city)
    if postcode_area:
        print(f" Highest value area: {highest_city} ({postcode_area}) £{highest_price:,.0f}")
    else:
        print(f" Highest value area: {highest_city} £{highest_price:,.0f}")
    return 

def city_inventory_analysis(df):
    # Use City column if available, otherwise fall back to Postcode_Area
    if 'City' in df.columns:
        inventory_counts = df.groupby('City').size()
        location_type = "City"
    else:
        inventory_counts = df.groupby('Postcode_Area').size()
        location_type = "Area"
    
    most_inventory_area = inventory_counts.idxmax()
    most_inventory_count = inventory_counts.max()
    
    # Find all locations with minimum count
    least_inventory_count = inventory_counts.min()
    least_inventory_areas = inventory_counts[inventory_counts == least_inventory_count].index.tolist()
    
    # Format display for most choices
    postcode_area = _get_postcode_for_city(df, most_inventory_area)
    if postcode_area:
        print(f"{location_type} with most choices: {most_inventory_area} ({postcode_area}) ({most_inventory_count} properties)")
    else:
        print(f"{location_type} with most choices: {most_inventory_area} ({most_inventory_count} properties)")
    
    # Format display for least choices
    if len(least_inventory_areas) == 1:
        postcode_area = _get_postcode_for_city(df, least_inventory_areas[0])
        if postcode_area:
            print(f"{location_type} with least choices: {least_inventory_areas[0]} ({postcode_area}) ({least_inventory_count} properties)")
        else:
            print(f"{location_type} with least choices: {least_inventory_areas[0]} ({least_inventory_count} properties)")
    else:
        # Show first few with postcode areas
        formatted_areas = []
        for area in least_inventory_areas[:3]:  # Show first 3
            postcode_area = _get_postcode_for_city(df, area)
            if postcode_area:
                formatted_areas.append(f"{area} ({postcode_area})")
            else:
                formatted_areas.append(str(area))
        
        areas_str = ", ".join(formatted_areas)
        if len(least_inventory_areas) > 3:
            areas_str += f" and {len(least_inventory_areas) - 3} others"
        print(f"{location_type}s with least choices: {areas_str} ({least_inventory_count} properties each)")
    
    return 

def price_comparison_by_new_built_status(df):
    new_built_avg_prices = df[df['New_built_indicator'] == 'Y']['Price'].mean()
    existing_built_avg_prices = df[df['New_built_indicator'] == 'N']['Price'].mean()
    print(f"Average price of new builds: £{new_built_avg_prices:,.0f}")
    print(f"Average price of existing properties: £{existing_built_avg_prices:,.0f}")
    return