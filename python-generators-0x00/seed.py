import sqlite3
import csv
import uuid
import os
from typing import Generator, Dict, Any

def connect_db():
    try:
        connection = sqlite3.connect('ALX_prodev.db')
        print("Successfully connected to SQLite database")
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to SQLite: {e}")
        return None
    
def create_database(connection):
    try:
        print("Database ALX_prodev.db created successfully")
    except sqlite3.Error as e:
        print(f"Error with database: {e}")
        
def connect_to_prodev():
    try:
        connection = sqlite3.connect('ALX_prodev.db')
        print("Successfully connected to ALX_prodev database")    
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None
    
def create_table(connection):
    try:
        cursor = connection.cursor()
    
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL
        )
        """
    
        cursor.execute(create_table_query)
        #creates index on user_id
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON user_data(user_id)")
        
        connection.commit()
        print("Table user_data created sucessfully")
        cursor.close() 
    
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
        
def insert_data(connection, csv_file_path):
    try:
        cursor = connection.cursor()
        
        if not os.path.exists(csv_file_path):
            print(f"CSV file {csv_file_path} not found")
            return 
        
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
        
            insert_query = """
            INSERT OR IGNORE INTO user_data (user_id, name, email, age)
            VALUES (?,?,?,?)
            """
            
            records_inserted = 0
            for row in csv_reader:
                user_data = (
                    str(uuid.uuid4()),
                    row['name'],
                    row['email'],
                    int(row['age'])
                )
                cursor.execute(insert_query, user_data)
                records_inserted += 1  
            
        connection.commit()
        print(f"Successfully inserted {records_inserted} records into user data table")
        cursor.close()
        
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        
def create_sample_csv():        
    
    sample_data = [
        ['name', 'email', 'age'],
        ['Dan Altenwerth Jr.', 'Molly59@gmail.com', '67'],
        ['Glenda Wisozk', 'Miriam21@gmail.com', '119'],
        ['Daniel Fahey IV', 'Delia.Lesch11@hotmail.com', '49'],
        ['Ronnie Bechtelar', 'Sandra19@yahoo.com', '22'],
        ['Alma Bechtelar', 'Shelly_Balistreri22@hotmail.com', '102'],
        ['John Doe', 'john.doe@email.com', '28'],
        ['Jane Smith', 'jane.smith@email.com', '32'],
        ['Bob Johnson', 'bob.johnson@email.com', '45'],
        ['Alice Brown', 'alice.brown@email.com', '29'],
        ['Charlie Wilson', 'charlie.wilson@email.com', '38']
    ]        
        
    with open('user_data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(sample_data)
        
    print("Sample user_data.csv created successfully")   
        
def stream_users_from_db(connection) -> Generator[Dict[str, Any], None, None]:
    try:
        #Sets row factory to return rows as dictionaries
        connection.row_factory = sqlite3.Row      
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_data")
        #Streams rows on by one
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            #convert sqlite3.Row to dictionary
            yield dict(row)
            
        cursor.close()
        
    except sqlite3.Error as e:
        print(f"Error streaming data from database: {e}")
        
def main():
    if not os.path.exists('user_data.csv'):
        create_sample_csv()
        
    connection = connect_db()
    if not connection:
        print("Failed to connect to SQLite database")
        return
        
    create_database(connection)
    
    create_table(connection)
    
    insert_data(connection, 'user_data.csv')
    
    for i, user in enumerate(stream_users_from_db(connection), 1):
        print(f"User {i}: {user}")
        if i >= 5: #limits output for testing
            break
        
    connection.close()
    print("SQLite database setup completed")
    
if __name__ == "__main__":
    main()