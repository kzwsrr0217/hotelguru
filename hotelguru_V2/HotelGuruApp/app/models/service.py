from __future__ import annotations

from typing import List, Optional
from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer

class Service(db.Model):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(30))
    price: Mapped[int] = mapped_column(Integer)
    
    hotel_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("hotels.id"))
    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="services")
    room: Mapped["Room"] = relationship("Room", back_populates="services")
