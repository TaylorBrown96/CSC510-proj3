#!/usr/bin/env python
"""Quick database setup script that doesn't rely on alembic."""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine
from eatsential.models.models import Base
from eatsential.config import settings

def setup_database():
    """Create database with all tables."""
    db_url = str(settings.DATABASE_URL)
    print(f"Setting up database at: {db_url}")
    
    engine = create_engine(db_url)
    
    # Create all tables based on models
    Base.metadata.create_all(engine)
    
    print("✅ Database setup complete!")
    print(f"📁 Database location: {db_url}")

if __name__ == "__main__":
    setup_database()
