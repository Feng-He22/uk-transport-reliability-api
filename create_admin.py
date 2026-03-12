from app.auth.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()

username = "admin"
password = "admin123"

user = db.query(User).filter(User.username == username).first()

if user:
    user.hashed_password = hash_password(password)
    user.role = "admin"
    user.is_active = True
    db.commit()
    print("Admin updated")
else:
    user = User(
        username=username,
        hashed_password=hash_password(password),
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    print("Admin created")