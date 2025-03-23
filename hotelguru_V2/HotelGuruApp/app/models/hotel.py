from __future__ import annotations

from typing import List
from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer

class Hotel(db.Model):
    __tablename__ = "hotels"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))  # Sz�lloda neve
    address: Mapped[str] = mapped_column(String(100))  # Sz�lloda c�me
    phone: Mapped[str] = mapped_column(String(15))  # Telefonsz�m

    rooms: Mapped[List["Room"]] = relationship("Room", back_populates="hotel")
    services: Mapped[List["Service"]] = relationship("Service", back_populates="hotel")
