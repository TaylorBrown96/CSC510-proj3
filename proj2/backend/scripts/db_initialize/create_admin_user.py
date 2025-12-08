"""Script to create an admin user for testing.

This script creates an admin user in the database.
Run this script to create your first admin user for testing.

Usage:
    cd /path/to/backend
    uv run python db_initialize/create_admin_user.py
"""

import uuid

from passlib.hash import argon2
from sqlalchemy.orm import Session

from eatsential.db.database import Base, SessionLocal, engine
from eatsential.models import AccountStatus, UserDB, UserRole


def create_admin_user(
    email: str = "admin@example.com",
    username: str = "admin",
    password: str = "Admin123!@#",  # noqa: S107
):
    """Create an admin user in the database.

    Args:
        email: Admin user email
        username: Admin username
        password: Admin password (must meet password requirements)

    """
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(UserDB).filter(UserDB.email == email).first()
        if existing_user:
            print(f"❌ User with email {email} already exists!")
            print(f"   Current role: {existing_user.role}")

            # Offer to update to admin
            response = input("Do you want to update this user to admin? (y/n): ")
            if response.lower() == "y":
                existing_user.role = UserRole.ADMIN
                existing_user.account_status = AccountStatus.VERIFIED
                existing_user.email_verified = True
                db.commit()
                print(f"✅ Updated {email} to admin role!")
                print_user_info(email, username, password)
            return

        # Create new admin user
        user_id = str(uuid.uuid4())
        password_hash = argon2.hash(password)

        admin_user = UserDB(
            id=user_id,
            email=email,
            username=username,
            password_hash=password_hash,
            role=UserRole.ADMIN,
            account_status=AccountStatus.VERIFIED,
            email_verified=True,
            verification_token=None,
            verification_token_expires=None,
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("✅ Admin user created successfully!")
        print_user_info(email, username, password)

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
        raise
    finally:
        db.close()


def print_user_info(email: str, username: str, password: str):
    """Print admin user credentials."""
    print("\n" + "=" * 60)
    print("Admin User Credentials")
    print("=" * 60)
    print(f"Email:    {email}")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print("Role:     admin")
    print("=" * 60)
    print("\n⚠️  IMPORTANT: Save these credentials in a secure location!")
    print("You can now login at: http://localhost:5173/login")
    print("After login, access admin panel at: http://localhost:5173/system-manage")
    print()


def list_all_users():
    """List all users in the database."""
    db: Session = SessionLocal()
    try:
        users = db.query(UserDB).all()
        if not users:
            print("No users found in database.")
            return

        print("\n" + "=" * 80)
        print("All Users in Database")
        print("=" * 80)
        print(f"{'Email':<30} {'Username':<20} {'Role':<10} {'Status':<15}")
        print("-" * 80)
        for user in users:
            email = user.email[:30]
            username = user.username[:20]
            role = user.role[:10]
            status = user.account_status[:15]
            print(f"{email:<30} {username:<20} {role:<10} {status:<15}")
        print("=" * 80)
        print()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create an admin user for testing")
    parser.add_argument(
        "--email",
        default="admin@example.com",
        help="Admin email (default: admin@example.com)",
    )
    parser.add_argument(
        "--username", default="admin", help="Admin username (default: admin)"
    )
    parser.add_argument(
        "--password",
        default="Admin123!@#",
        help="Admin password (default: Admin123!@#)",
    )
    parser.add_argument(
        "--list", action="store_true", help="List all users in database"
    )

    args = parser.parse_args()

    if args.list:
        list_all_users()
    else:
        create_admin_user(
            email=args.email, username=args.username, password=args.password
        )
