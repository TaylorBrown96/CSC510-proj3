# Database Initialization Scripts

This directory contains database initialization and seeding scripts for the Eatsential project.

## 🚀 Quick Start (Recommended)

For new developers setting up the project, use the **unified initialization script**:

```bash
# 1. Create empty database file
uv run python db_initialize/create_init_database.py

# 2. Apply database migrations
uv run alembic upgrade head

# 3. Seed database with all sample data
uv run python db_initialize/create_init_database.py --seed
```

This will set up:
- ✅ Admin user (email: `admin@example.com`, password: `Admin123!@#`)
- ✅ 38 allergens (FDA Big 9 + common allergens)
- ✅ 15 sample restaurants with 60 menu items
- ✅ 7 days of wellness logs for the admin user

## 📁 File Structure

```
db_initialize/
├── data/
│   ├── allergens.json          # Allergen data (FDA Big 9 + common)
│   └── restaurants.json         # Sample restaurant and menu data
├── create_init_database.py     # Main coordinator script
├── create_admin_user.py        # Admin user creation
├── init_allergens.py           # Allergen seeding (reads from JSON)
├── seed_restaurants.py         # Restaurant seeding (reads from JSON)
├── seed_wellness_logs.py       # Wellness logs seeding
├── verify_database.py          # Database verification utility
└── README.md                   # This file
```

## 🔧 Individual Scripts

Each script can be run independently for development and testing:

### Create Admin User

```bash
uv run python db_initialize/create_admin_user.py

# With custom credentials
uv run python db_initialize/create_admin_user.py --email admin@test.com --password MyPass123!
```

### Initialize Allergens

```bash
uv run python db_initialize/init_allergens.py
```

Loads allergen data from `data/allergens.json` and populates the database.

### Seed Restaurants

```bash
uv run python db_initialize/seed_restaurants.py
```

Loads restaurant data from `data/restaurants.json` and populates the database.

### Seed Wellness Logs

```bash
uv run python db_initialize/seed_wellness_logs.py
```

Creates 7 days of sample wellness logs for the admin user.

> **Note:** Requires admin user to exist first.

### Verify Database

```bash
uv run python db_initialize/verify_database.py
```

Checks database content and displays statistics.

## 📊 Sample Data Details

### Admin User
- **Email:** admin@example.com
- **Password:** Admin123!@#
- **Role:** ADMIN
- **Status:** VERIFIED

### Allergens (38 total)
Loaded from `data/allergens.json`:
- **FDA Big 9 Major Allergens:** milk, eggs, fish, shellfish, tree nuts, peanuts, wheat, soybeans, sesame
- **Specific allergens:** almonds, walnuts, cashews, shrimp, salmon, tuna, etc.
- **Other common allergens:** gluten, lactose, corn, mustard, celery, sulfites, etc.

### Restaurants (15 total)
Loaded from `data/restaurants.json`:
- Green Bowl Cafe (Healthy) - 4 menu items
- Sunny Sushi Bar (Japanese) - 4 menu items
- Mediterranean Delight (Mediterranean) - 4 menu items
- Spice Route Indian (Indian) - 4 menu items
- Taco Fiesta (Mexican) - 4 menu items
- Pasta Paradise (Italian) - 4 menu items
- Dragon Wok (Chinese) - 4 menu items
- Burger Station (American) - 4 menu items
- Thai Orchid (Thai) - 4 menu items
- Le Croissant (French) - 4 menu items
- Seoul Kitchen (Korean) - 4 menu items
- Poke Paradise (Hawaiian) - 4 menu items
- Vegan Heaven (Vegan) - 4 menu items
- Steak & Co (Steakhouse) - 4 menu items
- Breakfast Club (Breakfast) - 4 menu items

Each menu item includes:
- Name, description
- Calorie information
- Pricing

### Wellness Logs (21 total)
7 days of historical data for the admin user:
- **Mood logs:** Scores 5-9, varying by day
- **Stress logs:** Levels 1-5 (inverse of mood)
- **Sleep logs:** 7-8 hours duration, quality scores 6-9

## 🔄 Resetting the Database

To completely reset and reseed the database:

```bash
# 1. Remove existing database
rm eatsential.db  # or your configured database file

# 2. Recreate and seed
uv run python db_initialize/create_init_database.py
uv run alembic upgrade head
uv run python db_initialize/create_init_database.py --seed
```

## 🧪 Adding Custom Data

### Adding Allergens

Edit `data/allergens.json`:

```json
[
  {
    "name": "new allergen",
    "category": "category_name",
    "is_major_allergen": false,
    "description": "Description here"
  }
]
```

### Adding Restaurants

Edit `data/restaurants.json`:

```json
[
  {
    "name": "Restaurant Name",
    "address": "123 Main St",
    "cuisine": "Cuisine Type",
    "menu_items": [
      {
        "name": "Menu Item",
        "description": "Item description",
        "calories": 500.0,
        "price": 12.99
      }
    ]
  }
]
```

## 🛠️ Development Notes

When you modify database models:

1. Create a migration:
   ```bash
   uv run alembic revision --autogenerate -m "Description of changes"
   ```

2. Review the generated migration in `alembic/versions/`

3. Apply the migration:
   ```bash
   uv run alembic upgrade head
   ```

4. Update seed data in JSON files if needed

## 🔍 Troubleshooting

**"Admin user already exists"**
- The script detects existing data and skips creation
- This is normal and safe

**"Table already exists" errors**
- Run `uv run alembic upgrade head` first
- Ensure migrations are up to date

**Import errors**
- Make sure you're in the `backend/` directory
- Use `uv run python` instead of plain `python`
- Run `uv sync` to install dependencies

**JSON file not found**
- Check that `data/allergens.json` and `data/restaurants.json` exist
- Ensure you're running from the correct directory

## 📚 References

- [Database Setup Guide](../DATABASE_SETUP.md) - Detailed database configuration
- [Backend README](../README.md) - Overall backend documentation
- [Alembic Documentation](https://alembic.sqlalchemy.org/) - Database migrations
- [REFACTORING_SUMMARY.md](./REFACTORING_SUMMARY.md) - Details about the refactoring
