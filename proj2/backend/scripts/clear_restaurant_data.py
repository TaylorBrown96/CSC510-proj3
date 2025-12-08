"""
Clear all restaurant and menu item data from the database.

This script removes all restaurants and menu items, allowing you to reseed
with fresh data from Google Places API and CSV.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from eatsential.models.models import Restaurant, MenuItem
from eatsential.db.database import DATABASE_URL


def clear_restaurant_data():
    """Clear all restaurant and menu item data."""
    engine = create_engine(DATABASE_URL)
    
    with Session(engine) as db:
        # Count before deletion
        restaurant_count = db.query(Restaurant).count()
        menu_item_count = db.query(MenuItem).count()
        
        print(f"\n[INFO] Found {restaurant_count} restaurants and {menu_item_count} menu items")
        
        if restaurant_count == 0 and menu_item_count == 0:
            print("[INFO] Database is already empty")
            return
        
        # Delete all menu items first (due to foreign key constraint)
        print("[INFO] Deleting all menu items...")
        db.query(MenuItem).delete()
        
        # Delete all restaurants
        print("[INFO] Deleting all restaurants...")
        db.query(Restaurant).delete()
        
        db.commit()
        
        print(f"[SUCCESS] Cleared {restaurant_count} restaurants and {menu_item_count} menu items")
        print("[INFO] You can now reseed with fresh data using:")
        print("  uv run python scripts/seed_restaurants.py")
        print("  uv run python scripts/seed_menus_from_csv.py")


if __name__ == "__main__":
    clear_restaurant_data()
