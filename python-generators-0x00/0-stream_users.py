import sqlite3
from seed import connect_to_prodev

def stream_users():
    connection = connect_to_prodev()
    if not connection:
        return
    
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_data")
        
        for row in cursor:
            yield row
            
        cursor.close()
        connection.close()
        
    except sqlite3.Error as e:
        print(f"Error occurred: {e}")
        if connection:
            connection.close()
            
            
if __name__ == "__main__":
    print("Streaming users:")
    for row in stream_users():
        print(f"Name: {row['name']}, Email: {row['email']}, Age: {row['age']}")
        