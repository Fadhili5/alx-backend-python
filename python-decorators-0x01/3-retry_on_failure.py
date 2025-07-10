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

def retry_on_failure(retries=3,delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(retries + 1):
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    last_exception = e
                    
                    if attempt == retries:
                        raise last_exception
                    
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                    
                    #wait before retrying
                    time.sleep(delay)
                    
        return wrapper
    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)

def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

#### Attempt to fetch users with automatic retry on failure
users = fetch_users_with_retry()
print(users)
                    
    