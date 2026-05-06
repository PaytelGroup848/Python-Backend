from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str):
    password = password.encode("utf-8")[:72]  #  FIX
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    password = password.encode("utf-8")[:72]  #  FIX
    return pwd_context.verify(password, hashed)

def create_user(db: Session, email: str, password: str):
    user = User(
        email=email,
        password=hash_password(password),
        role="employee"   #  ADD THIS LINE
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user