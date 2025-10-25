"""
Database migration utilities for AyeSpy.
"""

import logging
from sqlalchemy import text
from .connection import get_db_manager

logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables."""
    try:
        db_manager = get_db_manager()
        db_manager.create_all_tables()
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        return False


def drop_tables():
    """Drop all database tables. Use with caution!"""
    try:
        db_manager = get_db_manager()
        db_manager.drop_all_tables()
        logger.warning("Database tables dropped")
        return True
    except Exception as e:
        logger.error(f"Failed to drop tables: {e}")
        return False


def create_indexes():
    """Create additional performance indexes."""
    try:
        db_manager = get_db_manager()
        engine = db_manager.engine
        
        # Additional indexes for better search performance
        indexes = [
            # Transcript search optimization
            "CREATE INDEX IF NOT EXISTS idx_segment_text_fts ON transcript_segments USING GIN(to_tsvector('english', text))",
            
            # Bill search optimization
            "CREATE INDEX IF NOT EXISTS idx_bill_title_fts ON bills USING GIN(to_tsvector('english', title))",
            "CREATE INDEX IF NOT EXISTS idx_bill_summary_fts ON bills USING GIN(to_tsvector('english', summary))",
            
            # Representative search optimization
            "CREATE INDEX IF NOT EXISTS idx_rep_name_fts ON representatives USING GIN(to_tsvector('english', full_name))",
            
            # Date range queries
            "CREATE INDEX IF NOT EXISTS idx_hearing_date_range ON hearings (date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_bill_introduced_range ON bills (introduced_date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_vote_date_range ON votes (vote_date DESC)",
        ]
        
        with engine.connect() as conn:
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                    conn.commit()
                except Exception as e:
                    # Some indexes might not be supported (e.g., GIN in SQLite)
                    logger.warning(f"Index creation failed (this is normal for some databases): {e}")
        
        logger.info("Additional indexes created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        return False


def reset_database():
    """Reset the entire database. Use with extreme caution!"""
    try:
        logger.warning("Resetting entire database...")
        drop_tables()
        create_tables()
        create_indexes()
        logger.info("Database reset completed successfully")
        return True
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        return False


def check_database_health():
    """Check database health and report any issues."""
    try:
        db_manager = get_db_manager()
        
        # Check connection
        if not db_manager.check_connection():
            return False, "Database connection failed"
        
        # Check tables
        tables = db_manager.get_table_info()
        expected_tables = {
            'representatives', 'committees', 'bills', 'bill_status_history',
            'hearings', 'transcript_segments', 'votes', 'data_update_log'
        }
        
        missing_tables = expected_tables - set(tables)
        if missing_tables:
            return False, f"Missing tables: {missing_tables}"
        
        # Check table row counts
        with db_manager.get_session() as session:
            for table_name in expected_tables:
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.scalar()
                    logger.info(f"Table {table_name}: {count} rows")
                except Exception as e:
                    logger.warning(f"Could not count rows in {table_name}: {e}")
        
        return True, "Database health check passed"
        
    except Exception as e:
        return False, f"Health check failed: {e}"


def initialize_database():
    """Initialize the database with tables and basic setup."""
    try:
        logger.info("Initializing database...")
        
        # Create tables
        if not create_tables():
            return False, "Failed to create tables"
        
        # Create additional indexes
        create_indexes()
        
        # Verify setup
        is_healthy, message = check_database_health()
        if not is_healthy:
            return False, f"Database setup verification failed: {message}"
        
        logger.info("Database initialization completed successfully")
        return True, "Database initialized successfully"
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False, f"Initialization failed: {e}" 