import mysql.connector

# --- Connection Details ---
USER = 'root'
PASSWORD = ''
HOST = 'localhost'
DATABASE_NAME = 'property_data2024'

try:
    # Connect directly to the database
    db_connection = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE_NAME
    )
    
    if db_connection.is_connected():
        cursor = db_connection.cursor()
        
        # Define the query to select one item
        query = "SELECT * FROM property_data LIMIT 1"
        
        print(f"Executing query: {query}")
        cursor.execute(query)
        
        # Fetch one record
        record = cursor.fetchone()
        
        if record:
            print("\n--- Found one record ---")
            print(f"Price: {record[0]}")
            print(f"Date: {record[1]}")
            print(f"Postcode: {record[2]}")
            print(f"Property Type: {record[3]}")
            print(f"New Built: {record[4]}")
            print(f"Tenure: {record[5]}")
            print(f"City: {record[6]}")
        else:
            print("No records found in the table.")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    # Clean up the connection
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'db_connection' in locals() and db_connection.is_connected():
        db_connection.close()
        print("\n🔌 MySQL connection closed.")
