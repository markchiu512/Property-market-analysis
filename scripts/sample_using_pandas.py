import pandas as pd
import mysql.connector

# --- Connection Details ---
USER = 'root'
PASSWORD = ''
HOST = 'localhost'
DATABASE_NAME = 'property_data2024'
TABLE_NAME = 'property_data'

db_connection = None
try:
    # 1. Connect directly to the database
    db_connection = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE_NAME
    )
    
    # 2. Define the query to select 100 records
    query = f"SELECT * FROM {TABLE_NAME} WHERE Postcode LIKE 'W2%'"
    
    print(f"🔄 Executing query to load 100 records into a DataFrame...")
    print(f"   Query: {query}")
    
    # 3. Use pd.read_sql to execute the query and load data into a DataFrame
    df = pd.read_sql(query, db_connection)
    breakpoint() 
    # 4. Display the results
    if not df.empty:
        print("\n✅ Successfully loaded data. DataFrame info:")
        df.info() # Displays a concise summary of the DataFrame
        
        print("\n--- First 5 Records ---")
        print(df.head()) # Displays the first 5 rows
        
        print(f"\nDataFrame shape: {df.shape}") # Confirms (rows, columns)
    else:
        print("🤷 No records found in the table.")

except mysql.connector.Error as err:
    print(f"❌ DATABASE ERROR: {err}")
except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")

finally:
    # 5. Clean up the connection
    if db_connection and db_connection.is_connected():
        db_connection.close()
