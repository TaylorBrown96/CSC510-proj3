"""Clear all wellness log data from the database.

This script deletes all records from mood_logs, stress_logs, and sleep_logs tables.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import text

from eatsential.db import SessionLocal


def clear_wellness_data() -> None:
    """Clear all wellness log data."""
    db = SessionLocal()
    try:
        # Delete all records from wellness tables
        tables = ["mood_logs", "stress_logs", "sleep_logs"]

        for table in tables:
            try:
                # S608: Hardcoded table names are safe
                query = f"DELETE FROM {table}"  # noqa: S608
                result = db.execute(text(query))
                db.commit()
                print(f"✓ Deleted {result.rowcount} records from {table}")
            except Exception as e:
                print(f"✗ Error deleting from {table}: {e}")
                db.rollback()

        print("\n✓ All wellness data has been cleared successfully!")

    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Clearing wellness data from database...")
    print("=" * 50)
    clear_wellness_data()
