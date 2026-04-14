from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    # one-to-many relationship: A user can save multiple notes
    notes = relationship("Notes", back_populates="owner")


class Notes(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)

    youtube_link = Column(Text)

    content = Column(Text)

    # Foreign key linking to the user
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="notes")
