#!/usr/bin/env python3
"""Verify database seeding was successful."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from eatsential.db.database import DATABASE_URL
from eatsential.models import (
    AllergenDB,
    MenuItem,
    MoodLogDB,
    Restaurant,
    SleepLogDB,
    StressLogDB,
    UserDB,
)


def verify_database():
    """Verify database content after seeding."""
    engine = create_engine(DATABASE_URL)
    session_local = sessionmaker(bind=engine)
    session = session_local()

    try:
        print("=" * 70)
        print("DATABASE VERIFICATION")
        print("=" * 70)

        # Count all entities
        counts = {
            "Users": session.query(UserDB).count(),
            "Allergens": session.query(AllergenDB).count(),
            "Restaurants": session.query(Restaurant).count(),
            "Menu Items": session.query(MenuItem).count(),
            "Mood Logs": session.query(MoodLogDB).count(),
            "Stress Logs": session.query(StressLogDB).count(),
            "Sleep Logs": session.query(SleepLogDB).count(),
        }

        print("\n📊 Entity Counts:")
        for entity, count in counts.items():
            print(f"   {entity}: {count}")

        # Verify admin user
        admin = (
            session.query(UserDB).filter(UserDB.email == "admin@example.com").first()
        )
        if admin:
            print("\n👤 Admin User:")
            print(f"   Email: {admin.email}")
            print(f"   Username: {admin.username}")
            print(f"   Role: {admin.role}")
            print(f"   Status: {admin.account_status}")
        else:
            print("\n❌ Admin user not found!")

        # Verify allergens
        major_allergens = (
            session.query(AllergenDB)
            .filter(AllergenDB.is_major_allergen == True)  # noqa: E712
            .count()
        )
        print(f"\n🔴 Major Allergens: {major_allergens}")

        # Sample restaurants
        restaurants = session.query(Restaurant).limit(3).all()
        if restaurants:
            print("\n🍽️  Sample Restaurants:")
            for r in restaurants:
                item_count = (
                    session.query(MenuItem)
                    .filter(MenuItem.restaurant_id == r.id)
                    .count()
                )
                print(f"   - {r.name} ({r.cuisine}): {item_count} items")

        print("\n" + "=" * 70)
        print("✅ DATABASE VERIFICATION COMPLETE")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        import traceback

        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    verify_database()
