from app.extensions import db, Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer, Float, Enum
from sqlalchemy import ForeignKey
from typing import Optional

class Reservation(Base):
    __tablename__ = 'reservations'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    guest_name: Mapped[str] = mapped_column(ForeignKey('users.name'), nullable=False)
    room_number: Mapped[int] = mapped_column(ForeignKey('rooms.number'), nullable=False)
    check_in_date: Mapped[str] = mapped_column(String, nullable=False)
    check_out_date: Mapped[str] = mapped_column(String, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[Enum] = mapped_column(Enum('booked', 'checked_in', 'checked_out', 'cancelled', name='status_enum'), nullable=False)
    
    def setStatus(self, status):
        self.status = status
