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
                    password_hash TEXT,
                    tokens INTEGER NOT NULL DEFAULT 100,
                    token_cap INTEGER NOT NULL DEFAULT 100,
                    last_token_refill INTEGER NOT NULL DEFAULT 0,
                    token_increment_interval INTEGER NOT NULL DEFAULT 5
                )
            ''')

    def create(self, file_id: str, filename: str, key: str, expire_at: int, password_hash: str | None = None) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO metadata (file_id, filename, key, expire_at, password_hash, tokens, token_cap, last_token_refill, token_increment_interval)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (file_id, filename, key, expire_at, password_hash, self.TOKEN_CAP, self.TOKEN_CAP, 0, self.TOKEN_INCREMENT_INTERVAL))
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
                'password_hash': row[4],
                'tokens': row[5],
                'token_cap': row[6],
                'last_token_refill': row[7],
                'token_increment_interval': row[8]
            }
        return {}

    def refill_tokens(self, file_id: str, count: int, update_time: int) -> None:
        if count <= 0:
            return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT tokens, token_cap FROM metadata WHERE file_id = ?', (file_id,))
            row = cursor.fetchone()
            if not row:
                return
            tokens, token_cap = row
            if count > 0:
                new_tokens = min(token_cap, tokens + count)
                cursor.execute('''
                    UPDATE metadata
                    SET tokens = ?, last_token_refill = ?
                    WHERE file_id = ?
                ''', (new_tokens, update_time, file_id))
                conn.commit()

    def consume_token(self, file_id: str, count: int = 1) -> bool:  
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT tokens FROM metadata WHERE file_id = ?', (file_id,))
            row = cursor.fetchone()
            if not row:
                return False
            tokens = row[0]
            if tokens >= count:
                new_tokens = tokens - count
                cursor.execute('''
                    UPDATE metadata
                    SET tokens = ?
                    WHERE file_id = ?
                ''', (new_tokens, file_id))
                conn.commit()
                return True
            else:
                return False
            
    def has_enough_token(self, file_id, count) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT tokens FROM metadata WHERE file_id = ?', (file_id,))
            row = cursor.fetchone()
            if not row:
                return False
            tokens = row[0]
            return tokens >= count


    def _get_all_data(self):
        """Helper method for testing: retrieves all data from the metadata table."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM metadata')
            rows = cursor.fetchall()
            return rows