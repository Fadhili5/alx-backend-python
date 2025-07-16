import sqlite3
from seed import connect_to_prodev

def paginate_users(page_size, offset):
    connection = connect_to_prodev()
    if not connection:
        return []
    
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        
        query = "SELECT * FROM user_data LIMIT ? OFFSET ?"
        cursor.execute(query, (page_size, offset))
        
        rows = cursor.fetchall()
        users = [dict(row) for row in rows]
        
        cursor.close()
        connection.close()
        
        print(f"Got {len(users)} users starting from position {offset}")
        return users
    
    except sqlite3.Error as e:
        print(f"Error: {e}")
        connection.close()
        return []
    

def lazy_paginate(page_size):
    """
    Only fetches the next page when needed
    """
    offset = 0
    
    while True:
        users = paginate_users(page_size, offset)
        
        if not users:
            print("No more users to fetch")
            break
        
        print(f"Here are the next {len(users)} users")
        yield users
        
        offset += page_size
        
if __name__ == "__main__":
    for page in lazy_paginate(page_size=5):
        print("Processing this page:")
        for user in page:
            print(f"Name: {user['name']} Age: {user['age']}")