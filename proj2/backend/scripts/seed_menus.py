"""
Script to scrape and populate menu items for all restaurants in the database.

This script:
1. Finds all restaurants without menu items
2. Attempts to scrape menu from their website
3. Falls back to sample menu items if scraping fails
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from eatsential.models.models import Restaurant, MenuItem, Base
from eatsential.services.menu_scraper import scrape_menu_for_restaurant
from eatsential.db.database import DATABASE_URL


async def seed_menus():
    """Scrape and seed menu items for all restaurants."""
    print("Starting menu scraping for all restaurants...")

    # Setup database
    db_url = str(DATABASE_URL)
    engine = create_engine(db_url)

    # Create tables if they don't exist
    Base.metadata.create_all(engine)

    db = Session(engine)

    try:
        # Get all restaurants
        restaurants = db.query(Restaurant).filter_by(is_active=True).all()
        print(f"Found {len(restaurants)} active restaurants")

        total_before = db.query(MenuItem).count()
        items_created = 0
        items_skipped = 0

        # Scrape menu for each restaurant
        for idx, restaurant in enumerate(restaurants, 1):
            print(f"[{idx}/{len(restaurants)}] Processing {restaurant.name}...", end=" ")
            try:
                created = await scrape_menu_for_restaurant(db, restaurant)
                if created:
                    items_created += len(created)
                    print(f"✓ ({len(created)} items)")
                else:
                    items_skipped += 1
                    print("✗ (no items)")
            except Exception as e:
                print(f"Error: {e}")
                items_skipped += 1

            # Rate limiting
            if idx % 5 == 0:
                await asyncio.sleep(1)

        total_after = db.query(MenuItem).count()

        print(f"\n✓ Menu seeding completed!")
        print(f"Menu items before: {total_before}")
        print(f"Menu items created: {items_created}")
        print(f"Restaurants skipped (no menu items): {items_skipped}")
        print(f"Menu items after: {total_after}")

    except Exception as e:
        print(f"Error during menu seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(seed_menus())
