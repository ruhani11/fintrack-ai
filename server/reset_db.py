# reset_db.py
import sqlite3
import os

DB_FILE = 'database.db'

# Delete old database if it exists
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print("Old database deleted.")

# Create new database and table
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT NOT NULL,
        month TEXT NOT NULL
    )
''')

conn.commit()
conn.close()
print("New database and table created successfully.")
