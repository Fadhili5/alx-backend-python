import sqlite3
import functools

#### decorator to lof SQL queries
def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = None
        
        if 'query' in kwargs:
            query = kwargs['query']
        # checks if there are positional arg ,and assumes first one might be query    
        elif args and isinstance(args[0], str):
            query = args[0]
            
        # Log the SQL query
        if query:
            print(f"Executing SQL query: {query}")
            
        return func(*args, **kwargs)
    
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect(r'C:\Users\HP\Desktop\decorators\users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")

print(f"Number of users found: {len(users)}")
if users:
    print("\nUser data:")
    print("-" * 50)
    for user in users:
        print(user)
        
else:
    print("No users found in the database")