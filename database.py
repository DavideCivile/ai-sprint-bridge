import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LogEntry:
    """Data class for log entries."""
    timestamp: str
    sender: str
    receiver: str
    sprint: int
    message_type: str
    content: str
    file_name: Optional[str] = None
    file_size: Optional[int] = None

class DatabaseManager:
    """Manages SQLite database for logging and data persistence."""
    
    DB_DIR = Path("database")
    DB_FILE = DB_DIR / "app.db"
    
    def __init__(self):
        """Initialize database manager."""
        self.db_path = self.DB_FILE
        self.DB_DIR.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    receiver TEXT NOT NULL,
                    sprint INTEGER NOT NULL,
                    message_type TEXT NOT NULL,
                    content TEXT,
                    file_name TEXT,
                    file_size INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sprint_id INTEGER NOT NULL,
                    sender TEXT NOT NULL,
                    receiver TEXT,
                    content TEXT NOT NULL,
                    message_hash TEXT UNIQUE,
                    synced BOOLEAN DEFAULT 0,
                    manual_approved BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sprint_id INTEGER NOT NULL,
                    sender TEXT NOT NULL,
                    receiver TEXT,
                    file_name TEXT NOT NULL,
                    file_size INTEGER,
                    file_path TEXT,
                    file_hash TEXT UNIQUE,
                    synced BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sprint_id INTEGER NOT NULL,
                    messages_synced INTEGER DEFAULT 0,
                    files_synced INTEGER DEFAULT 0,
                    sync_errors INTEGER DEFAULT 0,
                    last_sync TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def add_log(self, log_entry: LogEntry) -> bool:
        """Add a log entry."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO logs 
                (timestamp, sender, receiver, sprint, message_type, content, file_name, file_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                log_entry.timestamp,
                log_entry.sender,
                log_entry.receiver,
                log_entry.sprint,
                log_entry.message_type,
                log_entry.content,
                log_entry.file_name,
                log_entry.file_size
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error adding log: {e}")
            return False
    
    def get_logs(self, sprint_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get logs from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if sprint_id:
                cursor.execute('''
                    SELECT * FROM logs
                    WHERE sprint = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (sprint_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM logs
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error retrieving logs: {e}")
            return []
    
    def add_message(self, sprint_id: int, sender: str, content: str, message_hash: str) -> Optional[int]:
        """Add a message entry."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO messages 
                (sprint_id, sender, content, message_hash, synced)
                VALUES (?, ?, ?, ?, ?)
            ''', (sprint_id, sender, content, message_hash, 0))
            
            message_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Message added: {message_id}")
            return message_id
            
        except sqlite3.IntegrityError:
            logger.warning(f"Message already exists (duplicate): {message_hash}")
            return None
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            return None
    
    def get_pending_messages(self, sprint_id: int) -> List[Dict[str, Any]]:
        """Get messages pending sync."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM messages
                WHERE sprint_id = ? AND synced = 0
                ORDER BY created_at ASC
            ''', (sprint_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error retrieving pending messages: {e}")
            return []
    
    def mark_message_synced(self, message_id: int) -> bool:
        """Mark a message as synced."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE messages
                SET synced = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (message_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error marking message synced: {e}")
            return False
    
    def add_file(self, sprint_id: int, sender: str, file_name: str, file_size: int,
                file_path: str, file_hash: str) -> Optional[int]:
        """Add a file entry."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO files 
                (sprint_id, sender, file_name, file_size, file_path, file_hash, synced)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (sprint_id, sender, file_name, file_size, file_path, file_hash, 0))
            
            file_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"File entry added: {file_id}")
            return file_id
            
        except sqlite3.IntegrityError:
            logger.warning(f"File already exists (duplicate): {file_hash}")
            return None
        except Exception as e:
            logger.error(f"Error adding file: {e}")
            return None
    
    def get_pending_files(self, sprint_id: int) -> List[Dict[str, Any]]:
        """Get files pending sync."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM files
                WHERE sprint_id = ? AND synced = 0
                ORDER BY created_at ASC
            ''', (sprint_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error retrieving pending files: {e}")
            return []
    
    def mark_file_synced(self, file_id: int) -> bool:
        """Mark a file as synced."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE files
                SET synced = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (file_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error marking file synced: {e}")
            return False
    
    def get_sync_stats(self, sprint_id: int) -> Dict[str, Any]:
        """Get sync statistics for a sprint."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM sync_stats
                WHERE sprint_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            ''', (sprint_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return {
                "sprint_id": sprint_id,
                "messages_synced": 0,
                "files_synced": 0,
                "sync_errors": 0
            }
            
        except Exception as e:
            logger.error(f"Error retrieving sync stats: {e}")
            return {}
    
    def update_sync_stats(self, sprint_id: int, messages_synced: int = 0,
                         files_synced: int = 0, sync_errors: int = 0) -> bool:
        """Update sync statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sync_stats 
                (sprint_id, messages_synced, files_synced, sync_errors, last_sync)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (sprint_id, messages_synced, files_synced, sync_errors))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error updating sync stats: {e}")
            return False
    
    def get_message_count(self, sprint_id: int, sender: Optional[str] = None) -> int:
        """Get count of messages."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if sender:
                cursor.execute('''
                    SELECT COUNT(*) FROM messages
                    WHERE sprint_id = ? AND sender = ?
                ''', (sprint_id, sender))
            else:
                cursor.execute('''
                    SELECT COUNT(*) FROM messages
                    WHERE sprint_id = ?
                ''', (sprint_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception as e:
            logger.error(f"Error counting messages: {e}")
            return 0
    
    def get_file_count(self, sprint_id: int, sender: Optional[str] = None) -> int:
        """Get count of files."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if sender:
                cursor.execute('''
                    SELECT COUNT(*) FROM files
                    WHERE sprint_id = ? AND sender = ?
                ''', (sprint_id, sender))
            else:
                cursor.execute('''
                    SELECT COUNT(*) FROM files
                    WHERE sprint_id = ?
                ''', (sprint_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception as e:
            logger.error(f"Error counting files: {e}")
            return 0
    
    def clear_old_logs(self, days: int = 30) -> bool:
        """Clear logs older than specified days."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM logs
                WHERE datetime(created_at) < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Deleted {deleted} old log entries")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing old logs: {e}")
            return False


db_manager = DatabaseManager()
