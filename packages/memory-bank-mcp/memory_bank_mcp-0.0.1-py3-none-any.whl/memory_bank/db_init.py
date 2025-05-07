"""
Database initialization module for Memory Bank application.
"""
import sqlite3
from memory_bank.config import settings


def init_db():
    """Initialize SQLite database and tables if they don't exist."""
    conn = sqlite3.connect(settings.db_path)
    cursor = conn.cursor()

    # Table to store files and their content, linked to a project
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            file_name TEXT NOT NULL,
            content TEXT,
            UNIQUE(project_name, file_name) -- Ensure each file in a project is unique
        )
    ''')

    # Optional: Separate table for projects if needed to store project metadata
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS projects (
    #         name TEXT PRIMARY KEY
    #     )
    # ''')

    conn.commit()
    conn.close()
