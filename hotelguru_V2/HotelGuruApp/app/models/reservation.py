from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Integer, Date
from sqlalchemy import ForeignKey
from typing import List
from datetime import date
from sqlalchemy.exc import IntegrityError

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

    def create_reservation(user_id: int, room_id: int, start_date: date, end_date: date) -> Reservation:
        # Ellenőrzés: start_date < end_date
        if start_date >= end_date:
            raise ValueError("A kezdő dátum nem lehet korábban mint a vég dátum")

        # Ellenőrzés: user_id és room_id léteznek-e
        user = db.session.get(User, user_id)
        room = db.session.get(Room, room_id)
        if not user:
            raise ValueError(f"Felhasználó a következő id-val nem létezik: {user_id} ")
        if not room:
            raise ValueError(f"Szoba a következő id-val nem létezik: {room_id} ")
        
        if not room.is_available:
        raise ValueError(f"A szoba (id={room_id}) jelenleg nem elérhető.")

        # Új foglalás létrehozása
        new_reservation = Reservation(
            user_id=user_id,
            room_id=room_id,
            start_date=start_date,
            end_date=end_date,
            reservation_date=date.today()
        )

        try:
            db.session.add(new_reservation)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Nem sikerült létrehozni a foglalást.")

        return new_reservation

#példa hívásra:
#from datetime import date

##try:
#    new_reservation = create_reservation(
#        user_id=1,
#        room_id=101,
#        start_date=date(2025, 4, 3),
#        end_date=date(2025, 4, 10)
#    )
#    print(new_reservation)
#except ValueError as e:
#   print(f"Hiba: {e}")