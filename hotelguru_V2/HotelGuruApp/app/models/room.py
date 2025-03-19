from __future__ import annotations

from typing import List, Optional
from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer, Float

class Room(db.Model):
    __tablename__ = "rooms"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(20))  # Egyszerű szöveges típus (pl. "egyágyas", "kétágyas", "lakosztály")
    price: Mapped[float] = mapped_column(Float)  # Ár, lebegőpontos számként
    description: Mapped[Optional[str]] = mapped_column(String(100))  # Opcionális leírás
    is_available: Mapped[bool] = mapped_column(default=True)  # Foglalható-e a szoba
    
    hotel_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("hotels.id"))
    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="rooms")

    services: Mapped[List["Service"]] = relationship("Service", back_populates="room")


