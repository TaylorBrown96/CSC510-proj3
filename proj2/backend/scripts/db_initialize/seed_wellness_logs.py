"""Seed wellness logs for a user.

Creates 7 days of mood, stress, and sleep logs for testing purposes.
"""

import sys
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from eatsential.db.database import SessionLocal
from eatsential.models import MoodLogDB, SleepLogDB, StressLogDB, UserDB


def seed_wellness_logs_for_user(session: Session, user_id: str):
    """Create 7 days of wellness logs for the specified user.

    Args:
        session: Database session
        user_id: User ID to create logs for

    """
    print(f"\nSeeding wellness logs for user ID: {user_id}...")

    # Delete existing wellness logs for this user
    session.query(MoodLogDB).filter(MoodLogDB.user_id == user_id).delete()
    session.query(StressLogDB).filter(StressLogDB.user_id == user_id).delete()
    session.query(SleepLogDB).filter(SleepLogDB.user_id == user_id).delete()
    session.commit()

    # Generate logs for the past 7 days
    today = datetime.now(timezone.utc)
    logs_created = {"mood": 0, "stress": 0, "sleep": 0}

    for days_ago in range(7):
        # Calculate the timestamp for this day
        log_date = today - timedelta(days=days_ago)

        # Mood log with varying scores (simulating mood fluctuations)
        mood_score = 5 + (days_ago % 5)  # Score between 5-9
        mood_log = MoodLogDB(
            id=str(uuid.uuid4()),
            user_id=user_id,
            occurred_at_utc=log_date,
            mood_score=mood_score,
            encrypted_notes=None,  # Skip encryption for seed data
        )
        session.add(mood_log)
        logs_created["mood"] += 1

        # Stress log with varying levels (inverse of mood)
        stress_level = 10 - mood_score  # Inverse relationship
        stress_log = StressLogDB(
            id=str(uuid.uuid4()),
            user_id=user_id,
            occurred_at_utc=log_date,
            stress_level=stress_level,
            encrypted_triggers=None,  # Skip encryption for seed data
            encrypted_notes=None,  # Skip encryption for seed data
        )
        session.add(stress_log)
        logs_created["stress"] += 1

        # Sleep log with varying quality and duration
        duration_hours = 7.0 + (days_ago % 3) * 0.5  # 7.0 - 8.0 hours
        quality_score = 6 + (days_ago % 4)  # Score between 6-9
        sleep_log = SleepLogDB(
            id=str(uuid.uuid4()),
            user_id=user_id,
            occurred_at_utc=log_date,
            duration_hours=duration_hours,
            quality_score=quality_score,
            encrypted_notes=None,  # Skip encryption for seed data
        )
        session.add(sleep_log)
        logs_created["sleep"] += 1

    session.commit()

    print(
        f"✅ Created {logs_created['mood']} mood, "
        f"{logs_created['stress']} stress, "
        f"{logs_created['sleep']} sleep logs"
    )


def seed_wellness_logs():
    """Seed wellness logs for admin user (main entry point)."""
    db: Session = SessionLocal()

    try:
        # Find admin user
        admin_email = "admin@example.com"
        admin_user = db.query(UserDB).filter(UserDB.email == admin_email).first()

        if not admin_user:
            print(f"❌ Admin user {admin_email} not found!")
            print("   Please create admin user first using create_admin_user.py")
            sys.exit(1)

        print(f"\nSeeding wellness logs for user: {admin_email}")

        # Use the new function to seed logs
        seed_wellness_logs_for_user(db, admin_user.id)

        print("\n✅ Wellness logs seeding completed successfully!")

    except Exception as e:
        print(f"\n✗ Error seeding wellness logs: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Wellness Logs Seeding Script")
    print("=" * 60)
    seed_wellness_logs()
    print("\n" + "=" * 60)
    print("Seeding completed successfully!")
    print("=" * 60)
