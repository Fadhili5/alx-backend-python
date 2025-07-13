import asyncio
import aiosqlite
import os

async def async_fetch_users():
    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute("SELECT * FROM users")
        users = await cursor.fetchall()
        await cursor.close()
        
        print(f"async_fetch_users: Found {len(users)} users")
        return users
    
async def async_fetch_older_users():
    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute("SELECT * FROM users WHERE age > ?", (40,))
        older_users = await cursor.fetchall()
        await cursor.close()
        
        print(f"async_fetch_older_users: Found {len(older_users)} users older than 40")
        return older_users
    
async def fetch_concurrently():
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    print("Both queries completed concurrently!")
    return all_users, older_users

def ensure_database_exists(db_name):
    if not os.path.exists(db_name):
        print(f"Database {db_name} doesn't exists.")
        
        import sqlite3
        
        #Create database and users table
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
            ('Ivy Anderson', 'ivy.anderson@email.com', 43, 'Engineering'),
            ('Jack Wilson', 'jack.wilson@email.com', 52, 'Management'),
            ('Kate Brown', 'kate.brown@email.com', 47, 'Finance')
        ]
        
        cursor.executemany('''
            INSERT INTO users (name, email, age, department) VALUES (?, ?, ?, ?)
        ''', sample_users)
        
        conn.commit()
        conn.close()
        print("Database created successfully!")
        
    else:
        print(f"Database {db_name} already exists.")
        
def display_users(all_users, older_users):
    print("\nAll users:")
    print(f"{'ID':<3} {'Name':<15} {'Email':<25} {'Age':<4} {'Department':<12}")
    
    for users in all_users:
        print(f"{users[0]:<3} {users[1]:<15} {users[2]:<25} {users[3]:<4} {users[4]:<12}")
    
    print("Users older than 40:")    
    print(f"{'ID':<3} {'Name':<15} {'Email':<25} {'Age':<4} {'Department':<12}")
    
    for users in older_users:
        print(f"{users[0]:<3} {users[1]:<15} {users[2]:<25} {users[3]:<4} {users[4]:<12}")
        
async def main():
    ensure_database_exists("users.db")
    
    all_users, older_users = await fetch_concurrently()
    
    display_users(all_users, older_users)
    
if __name__ == "__main__":
    asyncio.run(main())