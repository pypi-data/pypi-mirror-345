"""
Database operations for Memory Bank.
"""
import sqlite3
from pathlib import Path
from typing import List, Optional


class Database:
    """Class to manage connections and operations with the SQLite database."""

    def __init__(self, db_path: Path):
        """Initialize database with path to SQLite file.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path

    def _connect(self):
        """Create a connection to the database."""
        return sqlite3.connect(self.db_path)

    def list_projects(self) -> List[str]:
        """Get list of unique project names from the files table.

        Returns:
            List of project names
        """
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT project_name FROM files ORDER BY project_name")
        projects = [row[0] for row in cursor.fetchall()]
        conn.close()
        return projects

    def project_exists(self, project_name: str) -> bool:
        """Check if a project exists (has at least one file).

        Args:
            project_name: Name of the project to check

        Returns:
            True if project exists, False otherwise
        """
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM files WHERE project_name = ? LIMIT 1", (project_name,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def list_files(self, project_name: str) -> List[str]:
        """Get list of file names for a specific project.

        Args:
            project_name: Name of the project

        Returns:
            List of file names in the project
        """
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT file_name FROM files WHERE project_name = ? ORDER BY file_name", (project_name,))
        files = [row[0] for row in cursor.fetchall()]
        conn.close()
        return files

    def read_file(self, project_name: str, file_name: str) -> Optional[str]:
        """Read the content of a specific file.

        Args:
            project_name: Name of the project containing the file
            file_name: Name of the file to read

        Returns:
            Content of the file or None if file doesn't exist
        """
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT content FROM files WHERE project_name = ? AND file_name = ?",
            (project_name, file_name)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def file_exists(self, project_name: str, file_name: str) -> bool:
        """Check if a specific file exists.

        Args:
            project_name: Name of the project
            file_name: Name of the file to check

        Returns:
            True if file exists, False otherwise
        """
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM files WHERE project_name = ? AND file_name = ? LIMIT 1",
            (project_name, file_name)
        )
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def write_file(self, project_name: str, file_name: str, content: str) -> bool:
        """Write a new file. Returns False if file already exists.

        Args:
            project_name: Name of the project to write file to
            file_name: Name of the new file
            content: Content of the new file

        Returns:
            True if successful, False if file already exists
        """
        if self.file_exists(project_name, file_name):
            return False  # Like original repo: don't overwrite

        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO files (project_name, file_name, content) VALUES (?, ?, ?)",
                (project_name, file_name, content)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Handle race condition (although unlikely with SQLite in this context)
            return False
        finally:
            conn.close()

    def update_file(self, project_name: str, file_name: str, content: str) -> bool:
        """Update content of an existing file. Returns False if file doesn't exist.

        Args:
            project_name: Name of the project containing the file
            file_name: Name of the existing file to update
            content: New content for the file

        Returns:
            True if successful, False if file doesn't exist
        """
        if not self.file_exists(project_name, file_name):
            return False

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE files SET content = ? WHERE project_name = ? AND file_name = ?",
            (content, project_name, file_name)
        )
        updated_rows = cursor.rowcount
        conn.commit()
        conn.close()
        return updated_rows > 0
