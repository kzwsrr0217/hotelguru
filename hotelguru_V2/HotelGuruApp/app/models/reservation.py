from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Integer, Date
from sqlalchemy import ForeignKey
from typing import List
from datetime import date

class Reservation(db.Model):
    __tablename__ = "reservations"
    id: Mapped[int] = mapped_column(primary_key=True)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    reservation_date: Mapped[date] = mapped_column(Date, default=date.today())

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="reservations")

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    room: Mapped["Room"] = relationship(back_populates="reservations")

    invoice: Mapped["Invoice"] = relationship(back_populates="reservation")

    def __repr__(self) -> str:
        return f"Reservation(id={self.id!r}, start_date={self.start_date!r}, end_date={self.end_date!r}, reservation_date={self.reservation_date!r})"
