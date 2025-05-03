import sqlite3
from typing import Dict, List, Optional

class SQLiteStorage:
    def __init__(self, db_path: str = 'bot.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def execute(self, query: str, params: tuple = ()):
        with self.conn:
            self.conn.execute(query, params)

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def close(self):
        self.conn.close()