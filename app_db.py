# database helper functions for spensmart , it handles SQLite connection and schema initialization

import sqlite3
from pathlib import Path

# Database file patj
DB_PATH = Path("database/spendsmart.db")

def get_db():   # open a connection to the Sqlite database, returns the connection object.
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # so we can access columns by name
    return conn 

def init_db():   #initialize the database with required tables 
    conn = get_db()
    cursor = conn.cursor()
    
# database helper functions for spensmart , it handles SQLite connection and schema initialization

import sqlite3
from pathlib import Path

# Database file patj
DB_PATH = Path("database/spendsmart.db")

def get_db():   # open a connection to the Sqlite database, returns the connection object.
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # so we can access columns by name
    return conn 

def init_db():   #initialize the database with required tables 
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            category TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")







