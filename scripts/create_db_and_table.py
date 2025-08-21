import mysql.connector
from mysql.connector import errorcode
import csv

# --- Configuration ---
USER = 'root'
PASSWORD = ''
HOST = 'localhost'
DATABASE_NAME = 'property_data2024'
TABLE_NAME = 'property_data'
RAW_CSV_PATH = 'data/raw/pp-2024.csv' # Path to your CSV file

# --- Main Setup Logic ---
db_connection = None
cursor = None
try:
    # 1. Connect and Create Database
    db_connection = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD)
    cursor = db_connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME} DEFAULT CHARACTER SET 'utf8'")
    db_connection.database = DATABASE_NAME
    print(f"✅ Database '{DATABASE_NAME}' is ready.")

    # 2. Create Table
    table_definition = (
        f"CREATE TABLE IF NOT EXISTS `{TABLE_NAME}` ("
        "  `Price` INT,"
        "  `Datetime` DATE,"
        "  `Postcode` VARCHAR(10),"
        "  `Property_Type` VARCHAR(50),"
        "  `New_built_indicator` CHAR(1),"
        "  `Tenure_Type` CHAR(1),"
        "  `City` VARCHAR(255)"
        ") ENGINE=InnoDB")
    cursor.execute(table_definition)
    print(f"✅ Table '{TABLE_NAME}' is ready.")

    # 3. Clear Existing Data from Table
    cursor.execute(f"DELETE FROM {TABLE_NAME}")
    print(f"🧹 Cleared existing data from '{TABLE_NAME}'.")
    
    # 4. Read CSV and Insert Data
    print(f"🔄 Reading data from '{RAW_CSV_PATH}'...")
    insert_rows = []
    with open(RAW_CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # next(reader) # Use this if your CSV has a header row
        for row in reader:
            # Assumes columns are: [some_id, price, date, postcode, type, new_build, tenure, city, ...]
            insert_rows.append((int(row[1]), row[2], row[3], row[4], row[5], row[6], row[7]))

    sql_insert_query = (
        f"INSERT INTO {TABLE_NAME} "
        "(Price, Datetime, Postcode, Property_Type, New_built_indicator, Tenure_Type, City) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
    
    cursor.executemany(sql_insert_query, insert_rows)
    db_connection.commit()
    print(f"✅ Successfully inserted {cursor.rowcount} rows into the database.")

except FileNotFoundError:
    print(f"❌ ERROR: The file was not found at '{RAW_CSV_PATH}'")
except mysql.connector.Error as err:
    print(f"❌ DATABASE ERROR: {err}")
except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")
finally:
    # 5. Clean up the connection
    if cursor:
        cursor.close()
    if db_connection and db_connection.is_connected():
        db_connection.close()
        print("🔌 MySQL connection closed.")
