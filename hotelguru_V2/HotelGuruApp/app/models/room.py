from __future__ import annotations

from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Integer, String, Float
from typing import List, Optional



class Room(db.Model):
    __tablename__ = "rooms"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    floor: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(String(200))
    price: Mapped[float] = mapped_column(Float)  # Ár, lebegőpontos számként
    is_available: Mapped[bool] = mapped_column(default=True)
    
    room_type_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("room_types.id"), nullable=False)
    room_type: Mapped["RoomType"] = relationship("RoomType", back_populates="rooms")

    reservations: Mapped[List["Reservation"]] = relationship(back_populates="room")

    
    

    def __repr__(self) -> str:
        return f"Room(id={self.id!r}, number={self.number!s}, type={self.room_type!s}, available={self.is_available!r})"
