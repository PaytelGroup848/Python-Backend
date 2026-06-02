from sqlalchemy import Column, Integer, String, ForeignKey   
from sqlalchemy.orm import relationship                      
from app.db.database import Base
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from datetime import datetime

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        index=True
    )

    password = Column(
        String
    )

    role = Column(
        String,
        default="employee"
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

# =========================
# PERMISSION MODELS 
# =========================

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String)
    permission_id = Column(Integer, ForeignKey("permissions.id"))

    permission = relationship("Permission")