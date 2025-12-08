#!/usr/bin/env python3
"""Initial database setup and seeding script.

This script creates the initial SQLite database file and seeds it with sample data
by coordinating other initialization scripts.

Usage:
    python create_init_database.py          # Create empty database
    python create_init_database.py --seed   # Seed with all sample data

"""

import os
import sys

from dotenv import load_dotenv

from eatsential.db.database import get_database_path


def main():
    """Initialize the database file."""
    print("Initializing database...")

    # Load environment variables
    load_dotenv()

    # Get database path
    db_path = get_database_path()

    # Check if database already exists
    if os.path.exists(db_path):
        print(f"Database already exists at: {db_path}")
        response = input("Do you want to recreate it? (y/N): ").strip().lower()
        if response in ["y", "yes"]:
            os.remove(db_path)
            print("Existing database removed.")
        else:
            print("Keeping existing database.")
            print("\nNext steps:")
            print("1. Run 'uv run alembic upgrade head' to apply any migrations")
            print("2. Optionally seed data by running this script with --seed flag")
            print("3. Start your FastAPI application")
            return

    try:
        # Create the database file (empty)
        # Tables will be created by Alembic migrations
        print(f"Creating database file at: {db_path}")

        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

        # Create an empty database file
        import sqlite3

        conn = sqlite3.connect(db_path)
        conn.close()

        print("✅ Database file created successfully!")
        print(f"📁 Database location: {db_path}")
        print("\nNext steps:")
        print("1. Run 'uv run alembic upgrade head' to apply any migrations")
        print("2. Optionally seed data by running this script with --seed flag")
        print("3. Start your FastAPI application")

    except Exception as e:
        print(f"❌ Error creating database: {e}")
        sys.exit(1)


def seed_data():
    """Seed the database with all sample data by calling individual scripts."""
    print("=" * 70)
    print("DATABASE SEEDING - Eatsential Quick Start")
    print("=" * 70)

    try:
        # Import seeding functions
        from create_admin_user import create_admin_user
        from init_allergens import init_allergens
        # NOTE: Restaurant seeding is handled separately via Google Places API and CSV data
        # from seed_restaurants import main as seed_restaurants_main
        from seed_wellness_logs import seed_wellness_logs

        # 1. Create admin user
        print("\n1️⃣  Creating admin user...")
        create_admin_user(
            email="admin@example.com",
            username="admin",
            password="Admin123!@#",
        )

        # 2. Seed allergens
        print("\n2️⃣  Seeding allergens...")
        init_allergens()

        # 3. Seed restaurants - SKIPPED (using Google Places + CSV instead)
        print("\n3️⃣  Skipping placeholder restaurant data...")
        print("   (Real restaurants will be seeded from Google Places API + CSV)")

        # 4. Seed wellness logs for admin user
        print("\n4️⃣  Seeding wellness logs...")
        seed_wellness_logs()

        print("\n" + "=" * 70)
        print("✅ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\n🚀 You can now:")
        print("   1. Start app: cd proj2 && bun run dev")
        print("   2. Login at: http://localhost:5173")
        print("   3. Use credentials: admin@example.com / Admin123!@#")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--seed":
        seed_data()
    else:
        main()
