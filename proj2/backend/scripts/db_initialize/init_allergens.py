"""Initialize allergen database with predefined allergens.

This script populates the allergen_database table with FDA Big 9 Major Allergens
and other common food allergens.
"""

import json
from pathlib import Path
from typing import Optional
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from eatsential.db.database import DATABASE_URL
from eatsential.models.models import AllergenDB


def load_allergen_data():
    """Load allergen data from JSON file."""
    data_file = Path(__file__).parent / "data" / "allergens.json"
    with open(data_file) as f:
        return json.load(f)


def init_allergens(database_url: Optional[str] = None):
    """Initialize allergen database with predefined allergens.

    Args:
        database_url: Database connection URL. If None, uses default from config.

    """
    # Get database URL
    if database_url is None:
        database_url = DATABASE_URL

    # Load allergen data
    allergen_data_list = load_allergen_data()

    # Create engine and session
    engine = create_engine(database_url)
    session_local = sessionmaker(bind=engine)
    db = session_local()

    try:
        added_count = 0
        skipped_count = 0

        print("Starting allergen initialization...")
        print(f"Total allergens to process: {len(allergen_data_list)}\n")

        for allergen_data in allergen_data_list:
            # Check if allergen already exists
            existing = (
                db.query(AllergenDB)
                .filter(AllergenDB.name == allergen_data["name"])
                .first()
            )

            if existing:
                print(f"⏭️  Skipped: '{allergen_data['name']}' (already exists)")
                skipped_count += 1
                continue

            # Create new allergen
            allergen = AllergenDB(
                id=str(uuid4()),
                name=allergen_data["name"],
                category=allergen_data["category"],
                is_major_allergen=allergen_data["is_major_allergen"],
                description=allergen_data["description"],
            )

            db.add(allergen)
            major_marker = "🔴" if allergen_data["is_major_allergen"] else "⚪"
            print(
                f"{major_marker} Added: '{allergen_data['name']}' "
                f"({allergen_data['category']})"
            )
            added_count += 1

        # Commit all changes
        db.commit()

        print(f"\n{'=' * 60}")
        print("✅ Allergen initialization complete!")
        print(f"   - Added: {added_count} allergens")
        print(f"   - Skipped: {skipped_count} allergens (already existed)")
        print(f"   - Total in database: {added_count + skipped_count}")
        print(f"{'=' * 60}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during initialization: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_allergens()
