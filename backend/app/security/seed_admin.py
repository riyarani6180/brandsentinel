
import getpass

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.user import User
from app.security.password import hash_password


def create_admin():
    db: Session = SessionLocal()

    try:
        print("\nBrandSentinel - Create Brand Admin\n")

        full_name = input("Enter admin full name: ").strip()
        email = input("Enter admin email: ").strip().lower()
        password = getpass.getpass("Enter admin password: ")

        if len(full_name) < 2:
            print("Error: Full name must contain at least 2 characters.")
            return

        if len(password) < 8:
            print("Error: Password must contain at least 8 characters.")
            return

        existing_user = db.query(User).filter(
            User.email == email
        ).first()

        if existing_user:
            print("Error: This email is already registered.")
            return

        admin = User(
            full_name=full_name,
            email=email,
            hashed_password=hash_password(password),
            role="BRAND_ADMIN",
            is_active=True
        )

        db.add(admin)
        db.commit()

        print("\nBrand Admin created successfully!")
        print("Email:", email)
        print("Role: BRAND_ADMIN")

    except Exception:
        db.rollback()
        print("Unable to create admin. Check your input and try again.")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
