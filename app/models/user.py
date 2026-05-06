from sqlalchemy import Column, Integer, String, ForeignKey   
from sqlalchemy.orm import relationship                      
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="employee")

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