from sqlalchemy import Column, Integer, Text
from pgvector.sqlalchemy import Vector

from app.db.database import Base

class Document(Base):

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)

    content = Column(Text)

    embedding = Column(Vector(384))