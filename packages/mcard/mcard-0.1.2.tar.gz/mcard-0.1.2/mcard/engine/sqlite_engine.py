import sqlite3
from typing import Optional, List
import logging
import os
from mcard.model.card import MCard, MCardFromData
from mcard.model.card_collection import Page
from mcard.engine.base import StorageEngine, DatabaseConnection
from mcard.config.config_constants import DEFAULT_PAGE_SIZE, MCARD_TABLE_SCHEMA, TRIGGERS

logger = logging.getLogger(__name__)

class SQLiteConnection(DatabaseConnection):
    def __init__(self, db_path: str):
        self.db_path = os.path.abspath(db_path)  # Ensure it's an absolute path
        self.conn: Optional[sqlite3.Connection] = None
        self.setup_database()  # Call the setup method during initialization
        
    def setup_database(self):
        """Check if the database file exists; if not, create it."""
        try:
            # Resolve the absolute path for the database
            if not os.path.isabs(self.db_path):
                # Get the absolute path of the project's base directory
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                self.db_path = os.path.normpath(os.path.join(base_dir, self.db_path))
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Create the database file if it doesn't exist
            if not os.path.exists(self.db_path):
                # Create a new database file
                self.conn = sqlite3.connect(self.db_path)
                self.conn.close()  # Close the connection after creating the file

            # Create the card table if it does not exist
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS card (
                    hash TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    g_time REAL,
                    file_type TEXT
                )
            ''')
            self.conn.commit()
        except PermissionError as e:
            logger.error(f"Permission error: {e}")
            logger.error(f"Unable to access or create database at {self.db_path}")
            raise
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error setting up database: {e}")
            raise
        
    def connect(self) -> None:
        logger.debug(f"Connecting to database at {self.db_path}")
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            logger.debug(f"Connection established to {self.db_path}")
            logger.debug(f"Database connection details: {self.conn}")
            # Check if the database is empty and initialize schema if necessary
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            if not tables:
                # Drop existing tables and triggers
                self.conn.execute("DROP TABLE IF EXISTS card")
                self.conn.execute("DROP TABLE IF EXISTS documents")
                for table_name, schema in MCARD_TABLE_SCHEMA.items():
                    logging.info(f"Executing SQL: {schema}")
                    self.conn.execute(schema)
                self.conn.commit()  # Ensure the schema is committed
                logger.debug(f"Database schema created successfully")
                for trigger in TRIGGERS:
                    logging.info(f"Executing SQL: {trigger}")
                    self.conn.execute(trigger)
                    self.conn.commit()  # Ensure the triggers are committed
        except sqlite3.Error as e:
            logger.error(f"Database error connecting to {self.db_path}: {e}")
            raise
        
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

class SQLiteEngine(StorageEngine):
    def __init__(self, connection: SQLiteConnection):
        self.connection = connection
        self.connection.connect()
        
    def __del__(self):
        self.connection.disconnect()
        
    def add(self, card: MCard) -> str:
        hash_value = str(card.hash)
        try:
            cursor = self.connection.conn.cursor()
            cursor.execute(
                "INSERT INTO card (hash, content, g_time) VALUES (?, ?, ?)",
                (hash_value, card.content, str(card.g_time))
            )
            self.connection.commit()
            logger.debug(f"Added card with hash {hash_value}")
            return hash_value
        except sqlite3.IntegrityError:
            raise ValueError(f"Card with hash {hash_value} and {str(card.g_time)} already exists, \n Content: {card.content[:-20]}")


    def get(self, hash_value: str) -> Optional[MCard]:
        cursor = self.connection.conn.cursor()
        cursor.execute("SELECT content, g_time, hash FROM card WHERE hash = ?", (str(hash_value),))
        row = cursor.fetchone()
        
        if not row:
            return None
            
        content, g_time, hash = row
        card = MCardFromData(content, hash, g_time) 
        return card
    
    def delete(self, hash_value: str) -> bool:
        cursor = self.connection.conn.cursor()
        cursor.execute("DELETE FROM card WHERE hash = ?", (str(hash_value),))
        self.connection.commit()
        return cursor.rowcount > 0
    
    def get_page(self, page_number: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Page:
        if page_number < 1:
            raise ValueError("Page number must be >= 1")
        if page_size < 1:
            raise ValueError("Page size must be >= 1")
            
        offset = (page_number - 1) * page_size
        
        cursor = self.connection.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM card")
        total_items = cursor.fetchone()[0]
        
        cursor.execute(
            "SELECT content, g_time, hash FROM card ORDER BY g_time DESC LIMIT ? OFFSET ?",
            (page_size, offset)
        )
        
        items = []
        for row in cursor.fetchall():
            content, g_time, hash = row  # Assuming the row contains these values
            content_bytes = content.encode('utf-8') if isinstance(content, str) else content
            card = MCardFromData(content_bytes, hash, g_time) 
            items.append(card)  # Append the card to the items list
        
        return Page(
            items=items,
            total_items=total_items,
            page_number=page_number,
            page_size=page_size,
            has_next=offset + len(items) < total_items,
            has_previous=page_number > 1
        )
    
    
    
    def search_by_string(self, search_string: str, page_number: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Page:
        """Search for cards by string in content, hash, or g_time"""
        if page_number < 1:
            raise ValueError("Page number must be >= 1")
        if page_size < 1:
            raise ValueError("Page size must be >= 1")

        offset = (page_number - 1) * page_size
        cursor = self.connection.conn.cursor()

        # Get total count of matching items
        cursor.execute("""
            SELECT COUNT(*) FROM card 
            WHERE hash LIKE ? OR g_time LIKE ? OR content LIKE ?
        """, (f"%{search_string}%", f"%{search_string}%", f"%{search_string}%"))
        total_items = cursor.fetchone()[0]

        # Get the actual items for the current page
        cursor.execute("""
            SELECT content, g_time, hash FROM card 
            WHERE hash LIKE ? OR g_time LIKE ? OR content LIKE ?
            ORDER BY g_time DESC LIMIT ? OFFSET ?
        """, (f"%{search_string}%", f"%{search_string}%", f"%{search_string}%", page_size, offset))

        items = []
        for row in cursor.fetchall():
            content, g_time, hash = row  # Assuming the row contains these values
            card = MCardFromData(content, hash, g_time) 
            items.append(card)

        has_next = total_items > (page_number * page_size)
        has_previous = page_number > 1

        return Page(
            items=items,
            total_items=total_items,
            page_number=page_number,
            page_size=page_size,
            has_next=has_next,
            has_previous=has_previous
        )

    def search_by_content(self, search_string: str, page_number: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Page:
        """Search for cards by string in content"""
        if page_number < 1:
            raise ValueError("Page number must be >= 1")
        if page_size < 1:
            raise ValueError("Page size must be >= 1")

        offset = (page_number - 1) * page_size
        cursor = self.connection.conn.cursor()

        # Get total count of matching items
        cursor.execute("""
            SELECT COUNT(*) FROM card 
            WHERE content LIKE ?
        """, (f"%{search_string}%",))
        total_items = cursor.fetchone()[0]

        # Get the actual items for the current page
        cursor.execute("""
            SELECT content, g_time, hash FROM card 
            WHERE content LIKE ?
            ORDER BY g_time DESC LIMIT ? OFFSET ?
        """, (f"%{search_string}%", page_size, offset))

        items = []
        for row in cursor.fetchall():
            content, g_time, hash = row  # Assuming the row contains these values
            content_bytes = content.encode('utf-8') if isinstance(content, str) else content
            card = MCardFromData(content_bytes, hash, g_time) 
            items.append(card)

        has_next = total_items > (page_number * page_size)
        has_previous = page_number > 1

        return Page(
            items=items,
            total_items=total_items,
            page_number=page_number,
            page_size=page_size,
            has_next=has_next,
            has_previous=has_previous
        )

    def clear(self) -> None:
        cursor = self.connection.conn.cursor()
        cursor.execute("DELETE FROM card")
        self.connection.commit()
    
    def count(self) -> int:
        cursor = self.connection.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM card")
        return cursor.fetchone()[0]

    def get_all(self, page_number: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Page:
        if page_number < 1:
            raise ValueError("Page number must be >= 1")
        if page_size < 1:
            raise ValueError("Page size must be >= 1")
            
        offset = (page_number - 1) * page_size
        
        cursor = self.connection.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM card")
        total_items = cursor.fetchone()[0]
        
        cursor.execute(
            "SELECT content, g_time, hash FROM card ORDER BY g_time DESC LIMIT ? OFFSET ?",
            (page_size, offset)
        )
        
        items = []
        for row in cursor.fetchall():
            content, g_time, hash = row  # Assuming the row contains these values
            content_bytes = content.encode('utf-8') if isinstance(content, str) else content
            card = MCardFromData(content_bytes, hash, g_time) 
            items.append(card)  # Append the card to the items list
                
        return Page(
            items=items,
            total_items=total_items,
            page_number=page_number,
            page_size=page_size,
            has_next=offset + len(items) < total_items,
            has_previous=page_number > 1
        )
