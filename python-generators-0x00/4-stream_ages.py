import sqlite3
from seed import connect_to_prodev

def stream_user_ages():
    connection = connect_to_prodev()
    if not connection:
        return
    
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data")
        
        for row in cursor:
            yield row['age']
            
        print("Finished streaming ages")
        
        cursor.close()
        connection.close()
        
    except sqlite3.Error as e:
        print(f"Error streaming ages from database: {e}")
        if connection:
            connection.close()
            
def average_user_age():
    """
    Calculate average age of users
    """
    total_age = 0
    user_count = 0
    
    for age in stream_user_ages():
        total_age += age
        user_count += 1
        
    if user_count == 0:
        average_age = 0
    else:
        average_age = total_age / user_count
        
    print(f"Average age of users: average age = {average_age:.2f}")
    
if __name__ == "__main__":
    average_user_age()