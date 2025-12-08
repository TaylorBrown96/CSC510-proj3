"""
Seed menu items for restaurants using authentic menu data from CSV.

This script reads authentic menu items from a CSV file and randomly assigns
3-7 items per restaurant based on matching cuisine types.
"""

import sys
import csv
import random
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from eatsential.models.models import Restaurant, MenuItem, Base
from eatsential.db.database import DATABASE_URL

# Path to the CSV file (try multiple locations)
CSV_PATHS = [
    Path(__file__).parent.parent / "authentic_menu_items.csv",  # Backend root (PREFERRED)
    Path.home() / "Downloads" / "authentic_menu_items.csv",  # User downloads
    Path(__file__).parent.parent.parent / "Downloads" / "authentic_menu_items.csv",  # Relative to project
]


def find_csv_file() -> Path:
    """Find the CSV file in possible locations."""
    for path in CSV_PATHS:
        if path.exists():
            return path
    return CSV_PATHS[0]  # Return default path for error message


def load_menu_items_from_csv(csv_path: Path = None) -> dict[str, list[dict]]:
    """
    Load menu items from CSV and group by cuisine type.
    
    Returns:
        Dictionary mapping cuisine type to list of menu items
    """
    if csv_path is None:
        csv_path = find_csv_file()
    
    menu_items_by_cuisine = {}
    
    if not csv_path.exists():
        print(f"[ERROR] CSV file not found at: {csv_path}")
        print(f"[ERROR] Searched in:")
        for path in CSV_PATHS:
            print(f"  - {path} {'✓ EXISTS' if path.exists() else '✗ NOT FOUND'}")
        return menu_items_by_cuisine
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cuisine = row['cusinetype'].strip()
            
            if cuisine not in menu_items_by_cuisine:
                menu_items_by_cuisine[cuisine] = []
            
            menu_items_by_cuisine[cuisine].append({
                'name': row['name'].strip(),
                'description': row['description'].strip(),
                'calories': int(row['calories']) if row['calories'] else None,
                'price': float(row['price']) if row['price'] else None,
            })
    
    return menu_items_by_cuisine


def seed_menus_from_csv():
    """
    Assign random menu items from CSV to restaurants based on cuisine type.
    """
    print("\n" + "=" * 70)
    print("SEEDING MENU ITEMS FROM CSV")
    print("=" * 70)
    
    print("\n[INFO] Loading authentic menu items from CSV...")
    menu_items_by_cuisine = load_menu_items_from_csv()
    
    if not menu_items_by_cuisine:
        print("[ERROR] No menu items loaded. Exiting.")
        csv_path = find_csv_file()
        print(f"[ERROR] Expected CSV at: {csv_path}")
        print("[ERROR] Please ensure authentic_menu_items.csv is in your Downloads folder or proj2/backend/")
        return
    
    print(f"[INFO] Loaded {sum(len(items) for items in menu_items_by_cuisine.values())} menu items across {len(menu_items_by_cuisine)} cuisines")
    print(f"[INFO] Available cuisines: {', '.join(sorted(menu_items_by_cuisine.keys()))}")
    
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    
    with Session(engine) as db:
        # Get all active restaurants
        restaurants = db.query(Restaurant).filter_by(is_active=True).all()
        print(f"\n[INFO] Found {len(restaurants)} active restaurants")
        
        if not restaurants:
            print("[WARNING] No active restaurants found. Please run seed_restaurants.py first.")
            return
        
        # Show cuisine distribution
        cuisine_counts = {}
        for r in restaurants:
            cuisine = r.cuisine or "None"
            cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1
        print(f"[INFO] Restaurant cuisine distribution:")
        for cuisine, count in sorted(cuisine_counts.items()):
            print(f"  - {cuisine}: {count} restaurants")
        
        created_count = 0
        skipped_count = 0
        dropped_count = 0
        
        for idx, restaurant in enumerate(restaurants, 1):
            # Check if restaurant already has menu items
            existing_items = db.query(MenuItem).filter_by(restaurant_id=restaurant.id).count()
            if existing_items > 0:
                print(f"[{idx}/{len(restaurants)}] {restaurant.name} - Skipped (already has {existing_items} items)")
                skipped_count += 1
                continue
            
            # Get cuisine type - normalize the name
            cuisine = restaurant.cuisine
            if not cuisine:
                print(f"[{idx}/{len(restaurants)}] {restaurant.name} - X (no cuisine type)")
                restaurant.is_active = False
                db.commit()
                dropped_count += 1
                continue
            
            # Try exact match first, then fuzzy match
            available_items = menu_items_by_cuisine.get(cuisine)
            
            if not available_items:
                # Try to find a close match (e.g., "Italian restaurant" -> "Italian")
                print(f"[{idx}/{len(restaurants)}] {restaurant.name} ({cuisine}) - Trying fuzzy match...")
                for key in menu_items_by_cuisine.keys():
                    if key.lower() in cuisine.lower() or cuisine.lower() in key.lower():
                        available_items = menu_items_by_cuisine[key]
                        print(f"    Matched '{cuisine}' to '{key}'")
                        break
            
            if not available_items:
                print(f"[{idx}/{len(restaurants)}] {restaurant.name} ({cuisine}) - X (no matching menu items)")
                print(f"    Available cuisines: {', '.join(sorted(menu_items_by_cuisine.keys()))}")
                restaurant.is_active = False
                db.commit()
                dropped_count += 1
                continue
            
            # Randomly select 3-7 items
            num_items = random.randint(3, min(7, len(available_items)))
            selected_items = random.sample(available_items, num_items)
            
            # Create menu items
            try:
                for item_idx, item_data in enumerate(selected_items):
                    menu_item = MenuItem(
                        id=f"{restaurant.id}_item_{item_idx}",
                        restaurant_id=restaurant.id,
                        name=item_data['name'][:200],
                        description=item_data['description'][:1000] if item_data['description'] else None,
                        price=item_data['price'],
                        calories=item_data['calories'],
                    )
                    db.add(menu_item)
                
                db.commit()
                print(f"[{idx}/{len(restaurants)}] {restaurant.name} ({cuisine}) - ✓ ({num_items} items)")
                created_count += 1
                
            except Exception as e:
                db.rollback()
                print(f"[{idx}/{len(restaurants)}] {restaurant.name} - ✗ (error: {e})")
                restaurant.is_active = False
                db.commit()
                dropped_count += 1
        
        print(f"\n[INFO] Menu seeding complete:")
        print(f"  Created: {created_count} restaurants")
        print(f"  Skipped: {skipped_count} restaurants (already had items)")
        print(f"  Dropped: {dropped_count} restaurants (no matching cuisine or error)")


if __name__ == "__main__":
    try:
        seed_menus_from_csv()
    except Exception as e:
        print(f"\n[ERROR] Failed to seed menus from CSV: {e}")
        import traceback
        traceback.print_exc()
