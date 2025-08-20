import pandas as pd
import mysql.connector
import csv

# this is the dataframe that we want to upload to the database
raw_path = 'data/raw/pp-2024.csv'

user = 'root'
passowrd = ''
host = 'localhost'
database = 'property_data2024'


mydb = mysql.connector.connect(
    host=host,
    user=user,
    password=passowrd,
    database=database
)

mycursor = mydb.cursor()
#create database if it doesn't exist
# mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")  

# create the table from the dataframe df 
#df = pd.read_csv(raw_path)
mycursor.execute(f"CREATE TABLE IF NOT EXISTS {database}.property_data ("
    "Price INT,  "
    "Datetime DATE,   "
    "Postcode VARCHAR(10), "
    "Property_Type VARCHAR(50), "
    "New_built_indicator CHAR(1), "
    "Tenure_Type CHAR(1), "
    "City VARCHAR(255))")

# delete all rows from the table if it exists
#mycursor.execute(f"DELETE FROM {database}.property_data")

# mycursor.execute(f"DELETE FROM {database}.property_data")

# insert_row = list()
# with open(raw_path, 'r') as f:
#     reader = csv.reader(f)
#     for row in reader:
#         insert_row.append([ int(row[1]), row[2], row[3], row[4], row[5], row[6], row[7]])

#     # Insert data into the table
#     mycursor.execute(f"INSERT INTO {database}.property_data "
#                      "(Price, Datetime, Postcode, Property_Type, "
#                      "New_built_indicator, Tenure_Type, City) "
#                      "VALUES (%s, %s, %s, %s, %s, %s, %s)", insert_row)
#     mydb.commit()
# breakpoint()

insert_row = list()
with open(raw_path, 'r') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header row
    for row in reader:
        insert_row.append((int(row[1]), row[2], row[3], row[4], row[5], row[6], row[7]))
    # Insert data into the table
    mycursor.executemany(f"INSERT INTO {database}.property_data "
                         "(Price, Datetime, Postcode, Property_Type, "
                         "New_built_indicator, Tenure_Type, City) "
                         "VALUES (%s, %s, %s, %s, %s, %s, %s)", insert_row)
    mydb.commit()
breakpoint()
