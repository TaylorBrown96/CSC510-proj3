"""
Seed script to populate restaurants from Google Places API within a 10-mile radius of NC State.

This script queries the Google Places API for restaurants in various cuisines within
a 10-mile radius and saves them to the database. It also pulls website URLs from place details.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import eatsential modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from eatsential.models.models import Restaurant, Base
from eatsential.services.restaurant_service import save_restaurant_from_google_places
from eatsential.db.database import DATABASE_URL

# Location constants
NC_STATE_LAT = 35.7847
NC_STATE_LNG = -78.6821
SEARCH_RADIUS_METERS = 16000  # 10 miles
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Common cuisines to seed
CUISINES = [
    "Italian restaurant",
    "Chinese restaurant",
    "Japanese restaurant",
    "Mexican restaurant",
    "Indian restaurant",
    "Thai restaurant",
    "Vietnamese restaurant",
    "Korean restaurant",
    "Mediterranean restaurant",
    "American restaurant",
    "French restaurant",
    "Spanish restaurant",
    "Greek restaurant",
    "Brazilian restaurant",
    "Turkish restaurant",
]


async def get_place_details(place_id: str) -> dict:
    """Fetch detailed information about a place including website."""
    if not GOOGLE_MAPS_API_KEY:
        raise RuntimeError("GOOGLE_MAPS_API_KEY is not configured")

    url = (
        "https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}"
        f"&fields=website,formatted_phone_number,opening_hours,business_status"
        f"&key={GOOGLE_MAPS_API_KEY}"
    )

    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()

    if data.get("status") == "OK":
        return data.get("result", {})
    return {}


async def search_restaurants_by_cuisine(cuisine: str) -> list[dict]:
    """Search for restaurants by cuisine type."""
    if not GOOGLE_MAPS_API_KEY:
        raise RuntimeError("GOOGLE_MAPS_API_KEY is not configured")

    url = (
        "https://maps.googleapis.com/maps/api/place/textsearch/json"
        f"?query={cuisine}"
        f"&location={NC_STATE_LAT},{NC_STATE_LNG}"
        f"&radius={SEARCH_RADIUS_METERS}"
        f"&key={GOOGLE_MAPS_API_KEY}"
    )

    all_results = []

    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()

    if "error_message" in data:
        print(f"Error searching for {cuisine}: {data['error_message']}")
        return []

    results = data.get("results", [])
    print(f"Found {len(results)} restaurants for '{cuisine}'")

    for result in results[:10]:  # LIMIT TO 10 PER CUISINE
        # Fetch place details to get website
        place_id = result.get("place_id")
        details = await get_place_details(place_id)

        all_results.append({
            "place_id": place_id,
            "name": result.get("name"),
            "formatted_address": result.get("formatted_address"),
            "rating": result.get("rating"),
            "price_level": result.get("price_level"),
            "location": result.get("geometry", {}).get("location"),
            "types": result.get("types", []),
            "geometry": result.get("geometry", {}),
            "website": details.get("website"),  # From place details
            "phone_number": details.get("formatted_phone_number"),
        })

    return all_results


async def seed_restaurants():
    """Main seed function."""
    print("Starting restaurant seed from Google Places API...")
    print(f"Location: NC State ({NC_STATE_LAT}, {NC_STATE_LNG})")
    print(f"Radius: 10 miles ({SEARCH_RADIUS_METERS} meters)")
    print(f"Cuisines: {CUISINES}\n")


    # Setup database
    db_url = str(DATABASE_URL)
    engine = create_engine(db_url)

    # Create tables if they don't exist
    Base.metadata.create_all(engine)

    db = Session(engine)

    try:
        all_places = {}
        total_before = db.query(Restaurant).count()

        # Search for all cuisines
        for cuisine_query in CUISINES:
            # Extract the cuisine name (e.g., "Italian restaurant" -> "Italian")
            cuisine_name = cuisine_query.replace(" restaurant", "").strip()
            
            print(f"Searching for: {cuisine_query}...")
            places = await search_restaurants_by_cuisine(cuisine_query)

            for place in places:
                place_id = place.get("place_id")
                if place_id and place_id not in all_places:
                    # Add the cuisine name to the place data
                    place["cuisine_type"] = cuisine_name
                    all_places[place_id] = place

            await asyncio.sleep(1)  # Rate limiting

        print(f"\nTotal unique restaurants found: {len(all_places)}")

        # Save all restaurants to database
        saved_count = 0
        for idx, (place_id, place_data) in enumerate(all_places.items(), 1):
            try:
                restaurant = save_restaurant_from_google_places(
                    db=db,
                    place_data=place_data,
                    cuisine=place_data.get("cuisine_type"),  # Use the cuisine type from query
                )
                if restaurant:
                    saved_count += 1
                    if idx % 10 == 0:
                        print(f"Saved {idx}/{len(all_places)} restaurants...")
            except Exception as e:
                print(f"Error saving restaurant {place_data.get('name')}: {e}")

        db.commit()
        total_after = db.query(Restaurant).count()

        print(f"\n✓ Seed completed!")
        print(f"Restaurants before: {total_before}")
        print(f"Restaurants saved: {saved_count}")
        print(f"Restaurants after: {total_after}")

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(seed_restaurants())
