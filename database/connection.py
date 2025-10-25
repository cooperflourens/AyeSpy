"""
Database connection management for AyeSpy.
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, database_url=None):
        """Initialize database manager.
        
        Args:
            database_url: SQLAlchemy database URL. If None, uses environment variable.
        """
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ayespy.db')
        self.engine = None
        self.SessionLocal = None
        self._setup_engine()
    
    def _setup_engine(self):
        """Setup SQLAlchemy engine with optimizations for SQLite."""
        if 'sqlite' in self.database_url:
            # SQLite optimizations for better performance
            self.engine = create_engine(
                self.database_url,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30,
                },
                poolclass=StaticPool,
                pool_pre_ping=True,
                echo=os.getenv('DEBUG', 'False').lower() == 'true'
            )
            
            # Enable foreign key constraints for SQLite
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=10000")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.close()
        else:
            # PostgreSQL or other databases
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=os.getenv('DEBUG', 'False').lower() == 'true'
            )
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info(f"Database engine initialized: {self.database_url}")
    
    def get_session(self):
        """Get a new database session."""
        return self.SessionLocal()
    
    def get_scoped_session(self):
        """Get a scoped session for thread safety."""
        return scoped_session(self.SessionLocal)
    
    def create_all_tables(self):
        """Create all tables defined in models."""
        from .models import Base
        Base.metadata.create_all(bind=self.engine)
        logger.info("All database tables created successfully")
    
    def drop_all_tables(self):
        """Drop all tables. Use with caution!"""
        from .models import Base
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("All database tables dropped")
    
    def check_connection(self):
        """Test database connection."""
        try:
            with self.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def get_table_info(self):
        """Get information about existing tables."""
        try:
            with self.engine.connect() as conn:
                from sqlalchemy import text
                if 'sqlite' in self.database_url:
                    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                else:
                    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
                
                tables = [row[0] for row in result]
                return tables
        except Exception as e:
            logger.error(f"Failed to get table info: {e}")
            return []
    
    def close(self):
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")


# Global database manager instance
db_manager = DatabaseManager()


def get_db():
    """Get database session for dependency injection."""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()


def get_db_manager():
    """Get the global database manager instance."""
    return db_manager 