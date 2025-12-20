from .base import DatabaseBase
import sqlite3
from helpers.custom_exceptions import DuplicateIDError

class SQLiteMetadata(DatabaseBase):

    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self._initialize_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metadata (
                    file_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    key TEXT NOT NULL,
                    expire_at INTEGER NOT NULL,
                    downloads INTEGER NOT NULL,
                    attempts INTEGER NOT NULL,
                    password_hash TEXT
                )
            ''')

    def create(self, file_id: str, filename: str, key: str, expire_at: int, downloads: int, attempts: int, password_hash: str) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO metadata (file_id, filename, key, expire_at, downloads, attempts, password_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (file_id, filename, key, expire_at, downloads, attempts, password_hash))
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed' in str(e):
                    raise DuplicateIDError from e
                else:
                    raise

    def get(self, file_id: str) -> dict:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM metadata WHERE file_id = ?', (file_id,))
            row = cursor.fetchone()
        if row:
            return {
                'file_id': row[0],
                'filename': row[1],
                'key': row[2],
                'expire_at': row[3],
                'downloads': row[4],
                'attempts': row[5],
                'password_hash': row[6]
            }
        return {}

    def increment_downloads(self, file_id: str) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE metadata SET downloads = downloads + 1 WHERE file_id = ?', (file_id,))

    def increment_attempts(self, file_id: str) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE metadata SET attempts = attempts + 1 WHERE file_id = ?', (file_id,))


    def _get_all_data(self):
        """Helper method for testing: retrieves all data from the metadata table."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM metadata')
            rows = cursor.fetchall()
            return rows