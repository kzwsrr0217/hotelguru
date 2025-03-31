import enum
from os import statvfs_result
from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Integer, Float, Date, String
from sqlalchemy import ForeignKey, Column, Table
from datetime import date
from typing import List
from app.models.reservation import Reservation
from app.models.service import Service
from sqlalchemy.exc import IntegrityError
from app.models.association_tables import invoice_service

class StatusEnum(enum.Enum):
    Canceled  = 0,
    Live      = 1,
    Colsed    = 2

class Invoice(db.Model):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float] = mapped_column(Float)
    issue_date: Mapped[date] = mapped_column(Date, default=date.today())

    reservation_id: Mapped[int] = mapped_column(ForeignKey("reservations.id"))
    reservation: Mapped["Reservation"] = relationship(back_populates="invoice")

    used_services: Mapped[str] = mapped_column(String(200), default="")
    services: Mapped[List["Service"]] = relationship(secondary=invoice_service, back_populates="invoices")

    status : Mapped[StatusEnum] = mapped_column(default = "Live")

    @classmethod
    def create_invoice(cls, reservation_id: int, service_ids: list[int] = None) -> "Invoice":
        reservation = db.session.get(Reservation, reservation_id)
        # 1. Ellenőrizzük, hogy a foglalás létezik-e.
        if not reservation:
            raise ValueError(f"Nincs foglalás ezzel az azonosítóval: {reservation_id}")
        
        # 2. Számoljuk ki a számla végösszegét.
        total_amount = 0
        for room in reservation.rooms:
            total_amount += room.price
        total_amount *= (reservation.end_date - reservation.start_date).days  # Szoba ára * eltelt napok
       
        # 3. Létrehozzuk az új számlát.
        invoice = cls(reservation_id=reservation_id, amount=total_amount)

        if service_ids:
            # 4. Ellenőrizzük, hogy a szolgáltatások léteznek-e.
            services = db.session.query(Service).filter(Service.id.in_(service_ids)).all()
            if len(services) != len(service_ids):
                raise ValueError("Egy vagy több szolgáltatás nem található.")
            
            # 5. Hozzáadjuk a szolgáltatásokat a számlához a segédtáblán keresztül.
            invoice.services.extend(services)

            # 6. Létrehozzuk a used_services stringet.
            used_service_ids_str = ",".join(map(str, service_ids))
            invoice.used_services = used_service_ids_str
            
            for service in services:
                invoice.amount += service.price

        # 7. Elmentjük az adatbázisba.
        try:
            db.session.add(invoice)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Nem sikerült létrehozni a számlát.")

        return invoice
    
    def add_services_to_invoice(self, service_ids: list[int]):
        # 1. Ellenőrizzük, hogy a szolgáltatások léteznek-e.
        services = db.session.query(Service).filter(Service.id.in_(service_ids)).all()
        if len(services) != len(service_ids):
            raise ValueError("Egy vagy több szolgáltatás nem található.")

        # 2. Hozzáadjuk a szolgáltatásokat a számlához a segédtáblán keresztül.
        self.services.extend(services)

        # 3. Frissítjük a used_services stringet.
        used_service_ids = [int(x) for x in self.used_services.split(",") if x]  # Meglévő ID-k listája
        for service_id in service_ids:
            print (service_id)
            if service_id not in used_service_ids:
                used_service_ids.append(service_id)
        self.used_services = ",".join(map(str, used_service_ids))

        # 4. Frissítjük a számla végösszegét.
        for service in services:
            if service.id not in [s.id for s in self.services]:
                self.amount += service.price
            else :
                raise ValueError(f"A szolgáltatás már szerepel a számlán: {service.name}")

        # 5. Elmentjük az adatbázisba.
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Nem sikerült hozzáadni a szolgáltatásokat a számlához.")

    def __repr__(self) -> str:
        return f"Invoice(id={self.id!r}, amount={self.amount!r}, issue_date={self.issue_date!r}, used_services={self.used_services!r})"
