# Restaurant and Menu Seeding Guide

This guide explains how to populate your database with real restaurants and menu items from the Raleigh area.

## Overview

The seeding process works in two steps:

1. **Seed Restaurants** - Queries Google Places API for restaurants within 10 miles of NC State
2. **Seed Menus** - Scrapes/generates menu items for each restaurant

## Prerequisites

- Google Maps API Key configured in `.env` file
- Dependencies installed: `uv run pip install -e .`
- Database initialized (already done if you've run the app)

## Step 1: Seed Restaurants from Google Places

This script queries Google Places API for restaurants across multiple cuisines within a 10-mile radius of NC State and saves them to the database with website URLs.

### Run the Script

```bash
cd backend
uv run python scripts/seed_restaurants.py
```

### What It Does

- Searches for restaurants across 15+ cuisines (Italian, Chinese, Japanese, Mexican, Indian, Thai, Vietnamese, Korean, Mediterranean, American, French, Spanish, Greek, Brazilian, Turkish)
- Fetches detailed information including:
  - Restaurant name
  - Address
  - Price level
  - Rating
  - Website URL
  - Phone number
  - Types/categories
- Deduplicates by place ID
- Saves to `restaurants` table
- Stores Google Place IDs for map embedding

### Expected Output

```
Starting restaurant seed from Google Places API...
Location: NC State (35.7847, -78.6821)
Radius: 10 miles (16000 meters)
Cuisines: 15 types

Searching for: Italian restaurant...
Found 20 restaurants for 'Italian restaurant'
...
✓ Seed completed!
Restaurants before: 5
Restaurants saved: 200
Restaurants after: 205
```

## Step 2: Create Menu Items

This script attempts to scrape menu items from each restaurant's website, or falls back to generating sample menu items if scraping fails.

### Run the Script

```bash
cd backend
uv run python scripts/seed_menus.py
```

### What It Does

For each restaurant:
1. Checks if menu items already exist
2. Attempts to scrape the restaurant's website for menu items
3. If scraping fails or no website URL, generates appropriate sample menu items based on cuisine type
4. Includes:
   - Item name
   - Description
   - Price
   - Cuisine-appropriate defaults (e.g., "Spaghetti Carbonara" for Italian restaurants)

### Expected Output

```
Starting menu scraping for all restaurants...
Found 205 active restaurants
[1/205] Processing Olive Garden Italian Restaurant...
[2/205] Processing Panda Express Chinese...
...
✓ Menu seeding completed!
Menu items before: 0
Menu items added: 820
Menu items after: 820
```

## Database Changes

A new Alembic migration has been created to add the `website_url` column to the `restaurants` table:

```bash
cd backend
uv run alembic upgrade head
```

This creates the column with type `VARCHAR(500)` and allows NULL values for restaurants without website URLs.

## Notes

### Rate Limiting

The seed scripts include rate limiting to respect Google Maps API quotas:
- 1-2 second delays between requests
- 2 second delays between pagination requests

### Sample Menu Items

If website scraping fails (which is common), the system generates sample menu items appropriate for the restaurant's cuisine:

- **Italian**: Spaghetti Carbonara, Risotto, Osso Buco, etc.
- **Mexican**: Carne Asada Tacos, Enchiladas, Chiles Rellenos, etc.
- **Japanese**: Salmon Nigiri, California Roll, Tonkatsu, etc.
- **Chinese**: Kung Pao Chicken, Mapo Tofu, Peking Duck, etc.
- **Indian**: Butter Chicken, Paneer Tikka Masala, Lamb Vindaloo, etc.
- **Thai**: Pad Thai, Green Curry, Tom Yum Soup, etc.
- **American**: Burgers, BBQ Ribs, Mac and Cheese, etc.

### Website URLs

Restaurant website URLs are pulled from Google Places API detail views and stored in the `website_url` column. These can be:
- Used for scraping more detailed menu items in the future
- Displayed in the UI for user reference
- Linked to from recommendation cards

### Google Place IDs

The restaurant `id` field is actually the Google Place ID (e.g., `ChIJ...`). This allows:
- Direct embedding in Google Maps iframes
- Future API calls to get updated information
- Consistency with the recommendation engine's Google Places integration

## Troubleshooting

### "GOOGLE_MAPS_API_KEY is not configured"

Make sure you have set `GOOGLE_MAPS_API_KEY` in your `.env` file:

```bash
GOOGLE_MAPS_API_KEY=your_actual_api_key_here
```

### "Error searching for Italian restaurant: INVALID_REQUEST"

Usually means the API key is invalid or quotas have been exceeded. Check your Google Cloud Console for:
- Valid API key
- Enabled APIs (Places API, Maps API)
- Billing enabled
- Rate limits

### Empty restaurants list after seeding

The script may have failed silently. Check:
1. API key is valid
2. No quota exceeded
3. Try searching for a specific cuisine manually first
4. Check database connection

### Menu items not being created

If menu items show 0 added:
1. Ensure restaurants were actually created in step 1
2. Check script output for specific error messages
3. Verify database connection
4. Try running again - restaurants without menus will be skipped on first run

## Advanced: Manual Seeding

If you prefer to add restaurants manually:

```python
from eatsential.services.restaurant_service import save_restaurant_from_google_places

place_data = {
    "place_id": "ChIJ...",
    "name": "Restaurant Name",
    "formatted_address": "123 Main St, Raleigh, NC",
    "website": "https://example.com",
    "types": ["restaurant", "food"],
    "geometry": {},
}

restaurant = save_restaurant_from_google_places(db, place_data, cuisine="Italian")
```

## Future Improvements

- [ ] Add Yelp API integration for more detailed menu data
- [ ] Implement menu scraping for specific restaurant chains
- [ ] Add nutritional information for menu items
- [ ] Support for restaurant hours and delivery info
- [ ] Image URLs for menu items
- [ ] User-contributed menu updates
