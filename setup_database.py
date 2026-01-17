"""
Database Setup Module
Downloads and sets up the Chinook SQLite database
"""
import os
import urllib.request
import sqlite3
from pathlib import Path


def download_chinook_database(db_path: str = "chinook.db") -> str:
    """
    Download the Chinook SQLite database from GitHub.
    
    Args:
        db_path: Path where the database should be saved
        
    Returns:
        Path to the downloaded database
    """
    # Check if database already exists
    if os.path.exists(db_path):
        print(f"✓ Database already exists at: {db_path}")
        return db_path
    
    print("Downloading Chinook database...")
    
    # URL to the Chinook SQLite database
    url = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"
    
    try:
        # Download the database
        urllib.request.urlretrieve(url, db_path)
        print(f"✓ Successfully downloaded database to: {db_path}")
        return db_path
    except Exception as e:
        print(f"✗ Error downloading database: {e}")
        raise


def verify_database(db_path: str) -> bool:
    """
    Verify that the database is valid and contains expected tables.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        True if database is valid
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n✓ Database verification successful!")
        print(f"✓ Found {len(tables)} tables: {', '.join(tables)}")
        
        # Get row counts for each table
        print("\nTable row counts:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"  - {table}: {count} rows")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Database verification failed: {e}")
        return False


def get_database_connection(db_path: str = "chinook.db") -> sqlite3.Connection:
    """
    Get a connection to the Chinook database.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        SQLite connection object
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


if __name__ == "__main__":
    # Setup database when run directly
    db_path = "chinook.db"
    
    print("=" * 60)
    print("Chinook Database Setup")
    print("=" * 60)
    
    # Download and verify
    download_chinook_database(db_path)
    verify_database(db_path)
    
    print("\n" + "=" * 60)
    print("✓ Setup complete!")
    print("=" * 60)
