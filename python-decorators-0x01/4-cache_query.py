import time 
import sqlite3
import functools

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect(r'C:\Users\HP\Desktop\decorators\users.db')
        try:
            result = func(conn, *args, **kwargs)
            return result
        finally:
            conn.close()
    return wrapper

query_cache = {}

def cache_query(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = None
        
        if 'query' in kwargs:
            query = kwargs['query']
        elif len(args) > 1 and isinstance(args[1], str):
            query = args[1]
            
        if query and query in query_cache:
            print(f"Cache hit for query: {query}")
            return query_cache[query]
        
        result = func(*args, **kwargs)
        
        if query:
            query_cache[query] = result
            print(f"Cache miss. Cache result for query: {query}.")
            
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call with cache cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
