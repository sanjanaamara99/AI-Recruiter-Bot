"""
Database initialization script.
Run this script to create all database tables.
"""

import logging
from database.db import init_database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Initialize database and create all tables."""
    try:
        logger.info("Starting database initialization...")
        init_database()
        logger.info("Database initialized successfully!")
        logger.info("All tables created.")
        
        print("\n" + "="*50)
        print("DATABASE INITIALIZATION COMPLETE")
        print("="*50)
        print("\nTables created:")
        print("  - candidates")
        print("  - resumes")
        print("  - skills")
        print("  - interview_sessions")
        print("  - questions")
        print("  - answers")
        print("  - reports")
        print("\nYou can now start the application with: python app.py")
        print("="*50 + "\n")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        print("\n" + "="*50)
        print("DATABASE INITIALIZATION FAILED")
        print("="*50)
        print(f"\nError: {str(e)}")
        print("\nPlease check:")
        print("  1. PostgreSQL is running")
        print("  2. Database credentials in .env are correct")
        print("  3. Database 'ai_interviewer' exists")
        print("="*50 + "\n")
        raise


if __name__ == "__main__":
    main()
