import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def _calculate_city_average_prices(df):
    average_prices = df.groupby('Postcode')['Price'].mean()
    return average_prices


def most_affordable_cities(average_prices):
    cheapest_city_avg = _calculate_city_average_prices(average_prices)
    cheapest_city = cheapest_city_avg.idxmin()
    cheapest_price = cheapest_city_avg[cheapest_city]
    print(f" Most affordable city: {cheapest_city} £{cheapest_price:,.0f}")
    return 

def highest_value_cities(average_prices):
    highest_city_avg = _calculate_city_average_prices(average_prices)
    highest_city = highest_city_avg.idxmax()
    highest_price = highest_city_avg[highest_city]
    print(f" Higheset_value_city: {highest_city} £{highest_price:,.0f}")
    return 

def city_inventory_analysis(df):
    inventory_counts = df.groupby('Postcode').size()
    most_inventory_city = inventory_counts.idxmax()
    most_inventory_count = inventory_counts.max()
    least_inventory_city = inventory_counts.idxmin()
    least_inventory_count = inventory_counts.min()
    print(f"Postcode with most choices: {most_inventory_city} ({most_inventory_count} properties)")
    print(f"Postcode with least choices: {least_inventory_city} ({least_inventory_count} properties)")
    return 
