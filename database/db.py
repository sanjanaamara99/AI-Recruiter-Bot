from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database.models import Base
from config import Config
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database connection and session management."""
    
    def __init__(self, database_url: str = None):
        """Initialize database connection."""
        self.database_url = database_url or Config.SQLALCHEMY_DATABASE_URI
        self.engine = None
        self.session_factory = None
        self.Session = None
    
    def init_db(self):
        """Initialize database engine and session factory."""
        try:
            self.engine = create_engine(
                self.database_url,
                echo=Config.SQLALCHEMY_ECHO,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20
            )
            
            self.session_factory = sessionmaker(bind=self.engine)
            self.Session = scoped_session(self.session_factory)
            
            logger.info("Database connection initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {str(e)}")
            raise
    
    def drop_tables(self):
        """Drop all database tables."""
        try:
            Base.metadata.drop_all(self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {str(e)}")
            raise
    
    def get_session(self):
        """Get a new database session."""
        return self.Session()
    
    def close_session(self):
        """Close the current session."""
        self.Session.remove()


# Global database instance
db = Database()


def init_database():
    """Initialize database and create tables."""
    db.init_db()
    db.create_tables()


def get_db_session():
    """Get database session for use in routes."""
    return db.get_session()
