import sqlite3
import os

class ExecuteQuery:
    def __init__(self, db_name: str, query: str, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params if params is not None else ()
        self.connection = None
        self.results = None
    
    def __enter__(self):
        print(f"Opening database connection to {self.db_name}")
        print(f"Executing query: {self.query}")
        print(f"With parameters: {self.params}")
        
        self.connection = sqlite3.connect(self.db_name)
        cursor = self.connection.cursor()
        
        cursor.execute(self.query, self.params)
        
        self.results = cursor.fetchall()
        
        print(f"Query executed successfully. Found {len(self.results)} rows.")
        
        return self.results
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection:
            print(f"Closing database connection to {self.db_name}")
            self.connection.close()
        
        if exc_type:
            print(f"An exception occurred: {exc_value}")
        
        return None

def ensure_database_exists(db_name):
    """
    Check if database exists and create it with users table if it doesn't.
    
    Args:
        db_name (str): Path to the database file
    """
    if not os.path.exists(db_name):
        print(f"Database {db_name} doesn't exist. Creating it...")
        
        # Create database and users table
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                age INTEGER,
                department TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        sample_users = [
            ('John Doe', 'john.doe@email.com', 28, 'Engineering'),
            ('Jane Smith', 'jane.smith@email.com', 32, 'Marketing'),
            ('Bob Johnson', 'bob.johnson@email.com', 45, 'Sales'),
            ('Alice Brown', 'alice.brown@email.com', 29, 'Engineering'),
            ('Charlie Wilson', 'charlie.wilson@email.com', 38, 'HR'),
            ('Diana Davis', 'diana.davis@email.com', 26, 'Design'),
            ('Frank Miller', 'frank.miller@email.com', 41, 'Engineering'),
            ('Grace Taylor', 'grace.taylor@email.com', 33, 'Marketing'),
            ('Henry Clark', 'henry.clark@email.com', 22, 'Sales'),
            ('Ivy Anderson', 'ivy.anderson@email.com', 35, 'Engineering')
        ]
        
        cursor.executemany('''
            INSERT INTO users (name, email, age, department) VALUES (?, ?, ?, ?)
        ''', sample_users)
        
        conn.commit()
        conn.close()
        print("Database created successfully!")
    else:
        print(f"Database {db_name} already exists.")

if __name__ == "__main__":
    ensure_database_exists("users.db")
    
    with ExecuteQuery("users.db", "SELECT * FROM users WHERE age > ?", (25,)) as results:
        print(f"{'ID':<3} {'Name':<15} {'Email':<25} {'Age':<4} {'Department':<12} {'Created':<20}")
        
        for user in results:
            print(f"{user[0]:<3} {user[1]:<15} {user[2]:<25} {user[3]:<4} {user[4]:<12} {user[5]:<20}")
        
        if not results:
            print("No users found matching the criteria.")
    
    print("Query executed successfully!")
