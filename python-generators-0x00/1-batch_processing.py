import sqlite3
from seed import connect_to_prodev

def stream_users_in_batches(batch_size):
    connection = connect_to_prodev()
    if not connection:
        return
    
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_data")
        
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            batch_dict = [dict(row) for row in rows]
            print(f"fetched {len(batch_dict)} users")
            yield batch_dict
            
        cursor.close()
        connection.close()
        
    except sqlite3.Error as e:
        print(f"Error streaming data from database: {e}")
        if connection:
            connection.close()
            
def batch_processing(batch_size):
    batch_count = 0
    
    for batch in stream_users_in_batches(batch_size):
        batch_count += 1
        users_over_25 = []
                
        print(f"Processing batch {batch_count}")
        
        for user in batch:
            if user['age'] > 25:
                users_over_25.append(user)
                
        print(f"Users in batch: {len(batch)}")
        print(f"Users over 25 in batch {len(users_over_25)}")
        for user in users_over_25:
            print(f"User: {user['name']} - Age: {user['age']}")
            
if __name__ == "__main__":
    batch_processing(batch_size=5)