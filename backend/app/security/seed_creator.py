
import getpass

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.user import User
from app.security.password import hash_password


def create_creator():
    db: Session = SessionLocal()

    try:
        print("\nBrandSentinel - Create Creator Account\n")

        full_name = input("Enter creator full name: ").strip()
        email = input("Enter creator email: ").strip().lower()
        password = getpass.getpass("Enter creator password: ")

        if len(full_name) < 2 or len(password) < 8:
            print("Name must have at least 2 characters and password at least 8.")
            return

        existing_user = db.query(User).filter(
            User.email == email
        ).first()

        if existing_user:
            print("This email is already registered.")
            return

        creator = User(
            full_name=full_name,
            email=email,
            hashed_password=hash_password(password),
            role="CREATOR",
            is_active=True
        )

        db.add(creator)
        db.commit()

        print("\nCreator account created successfully!")
        print("Email:", email)
        print("Role: CREATOR")

    except Exception as e:
        db.rollback()
        print("Error:", e)

    finally:
        db.close()


if __name__ == "__main__":
    create_creator()
