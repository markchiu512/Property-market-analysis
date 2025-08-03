import pandas as pd
import numpy as np

def generate_property_data():

    properties = []

    date_range = pd.date_range(start='2024-01-01', end='2024-12-31', freq="D").strftime('%Y-%m-%d')

    for i in range(1000):
        
    
        random_price = np.random.randint(100000, 2000000)

        
        random_date = np.random.choice(date_range)

        postcode = ['AB', 'AL', 'B', 'BA', 'BB', 'BD', 'BH', 'BL', 'BN', 'BR',
                    'BS', 'BT', 'CA', 'CB', 'CF', 'CH', 'CM', 'CO', 'CR', 'CT', 
                    'CV', 'CW', 'DA', 'DD', 'DE', 'DG', 'DH', 'DL', 'DN', 'DT', 
                    'DY', 'E', 'EC', 'EH', 'EN', 'EX', 'FK', 'FY', 'G', 'GL', 
                    'GU', 'GY', 'HA', 'HD', 'HG', 'HP', 'HR', 'HS', 'HU', 'HX', 
                    'IG', 'IM', 'IP', 'IV', 'JE', 'KA', 'KT', 'KW', 'KY', 'L', 
                    'LA', 'LD', 'LE', 'LL', 'LN', 'LS', 'LU', 'M', 'ME', 'MK', 
                    'ML', 'N', 'NE', 'NG', 'NN', 'NP', 'NR', 'NW', 'OL', 'OX', 
                    'PA', 'PE', 'PH', 'PL', 'PO', 'PR', 'RG', 'RH', 'RM', 'S', 
                    'SA', 'SE', 'SG', 'SK', 'SL', 'SM', 'SN', 'SO', 'SP', 'SR', 
                    'SS', 'ST', 'SW', 'SY', 'TA', 'TD', 'TF', 'TN', 'TQ', 'TR', 
                    'TS', 'TW', 'UB', 'W', 'WA', 'WC', 'WD', 'WF', 'WN', 'WR', 
                    'WS', 'WV', 'YO', 'ZE']
        random_postcode = np.random.choice(postcode)

        property_types = ['F', 'D', 'S', 'T']
        random_property_type = np.random.choice(property_types)

        new_built_types = ['Y', 'N']
        random_new_built = np.random.choice(new_built_types)


        tenure_types = ['F', 'L']
        random_tenure_type = np.random.choice(tenure_types)




        property_data = [
            int(random_price), 
            str(random_date),
            str(random_postcode), 
            str(random_property_type),
            str(random_new_built),
            str(random_tenure_type)]
        
        properties.append(property_data)

        
    columns = ['Price', 'Date', 'Postcode', 'Property Type', 'New built indicator', 'Tenure Type']
    df = pd.DataFrame(properties, columns=columns)

    df.to_csv('../data/processed/property_data.csv', index=False)
    print(f"Generated {len(df)} properties and saved to property_data.csv")
    print("\nSample data:")
    print(df.head())

if __name__ == "__main__":
    df = generate_property_data()