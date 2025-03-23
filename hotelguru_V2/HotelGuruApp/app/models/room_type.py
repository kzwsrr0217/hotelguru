from __future__ import annotations

from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String
from typing import List

class RoomType(db.Model):
    __tablename__ = "room_types"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    rooms: Mapped[List["Room"]] = relationship("Room", back_populates="room_type")

    def __repr__(self) -> str:
        return f"RoomType(id={self.id!r}, name={self.name!s})"
