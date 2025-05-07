import duckdb
from typing import Optional, List, Union
import logging
from mcard.model.card import MCard
from mcard.model.card_collection import Page
from mcard.engine.base import StorageEngine, DatabaseConnection
from mcard.config.config_constants import DEFAULT_PAGE_SIZE, MCARD_TABLE_SCHEMA


logger = logging.getLogger(__name__)

class DuckDBConnection(DatabaseConnection):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[duckdb.DuckDBPyConnection] = None
        
    def connect(self) -> None:
        self.conn = duckdb.connect(self.db_path)
        self.conn.execute(MCARD_TABLE_SCHEMA)
        self.conn.commit()
    
    def disconnect(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None
            
    def commit(self) -> None:
        if self.conn:
            self.conn.commit()
            
    def rollback(self) -> None:
        if self.conn:
            self.conn.rollback()

class DuckDBEngine(StorageEngine):
    def __init__(self, connection: DuckDBConnection):
        self.connection = connection
        self.connection.connect()
        
    def __del__(self):
        self.connection.disconnect()
        
    def add(self, card: MCard) -> str:
        hash_value = str(card.hash)
        try:
            self.connection.conn.execute(
                "INSERT INTO card (hash, content, g_time) VALUES (?, ?, ?)",
                [hash_value, card.content, str(card.g_time)]
            )
            self.connection.commit()
            logger.debug(f"Added card with hash {hash_value}")
            return hash_value
        except duckdb.ConstraintException:
            raise ValueError(f"Card with hash {hash_value} already exists")


    def get(self, hash_value: str) -> Optional[MCard]:
        result = self.connection.conn.execute(
            "SELECT content, g_time FROM card WHERE hash = ?", [str(hash_value)]
        ).fetchone()
        
        if not result:
            return None
            
        content, g_time = result
        card = MCard(content)
        return card
    
    def delete(self, hash_value: str) -> bool:
        result = self.connection.conn.execute(
            "DELETE FROM card WHERE hash = ? RETURNING 1", [str(hash_value)]
        ).fetchall()
        self.connection.commit()
        return len(result) > 0
    
    def get_page(self, page_number: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Page:
        if page_number < 1:
            raise ValueError("Page number must be >= 1")
        if page_size < 1:
            raise ValueError("Page size must be >= 1")
            
        offset = (page_number - 1) * page_size
        
        total_items = self.connection.conn.execute(
            "SELECT COUNT(*) FROM card"
        ).fetchone()[0]
        
        results = self.connection.conn.execute(
            "SELECT content, g_time FROM card ORDER BY g_time DESC LIMIT ? OFFSET ?",
            [page_size, offset]
        ).fetchall()
        
        items = [MCard(row[0]) for row in results]
        
        return Page(
            items=items,
            total_items=total_items,
            page_number=page_number,
            page_size=page_size,
            has_next=offset + len(items) < total_items,
            has_previous=page_number > 1
        )
    
    
    def search_by_string(self, search_string: str, page_number: int = 1, page_size: int = 10) -> Page:
        offset = (page_number - 1) * page_size
        search_string = f'%{search_string}%'  # Prepare for LIKE query
        
        cursor = self.connection.conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM card WHERE CAST(hash AS VARCHAR) LIKE ? OR CAST(g_time AS VARCHAR) LIKE ?",
            (search_string, search_string)
        )
        total_items = cursor.fetchone()[0]
        
        cursor.execute(
            "SELECT content, hash, g_time FROM card WHERE CAST(hash AS VARCHAR) LIKE ? OR CAST(g_time AS VARCHAR) LIKE ? ORDER BY g_time DESC LIMIT ? OFFSET ?",
            (search_string, search_string, page_size, offset)
        )
        
        items = [MCard(row[0].decode('utf-8')) for row in cursor.fetchall()]
        
        return Page(
            items=items,
            total_items=total_items,
            page_number=page_number,
            page_size=page_size,
            has_next=offset + len(items) < total_items,
            has_previous=page_number > 1
        )
    
    def clear(self) -> None:
        self.connection.conn.execute("DELETE FROM card")
        self.connection.commit()
    
    def count(self) -> int:
        return self.connection.conn.execute("SELECT COUNT(*) FROM card").fetchone()[0]
