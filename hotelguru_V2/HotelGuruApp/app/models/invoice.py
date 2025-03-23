from app.extensions import db, Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Integer, Float, Date
from sqlalchemy import ForeignKey, Column, Table
from datetime import date
from typing import List

invoice_service = db.Table(
    "invoice_service",
    Column("invoice_id", ForeignKey("invoices.id")),
    Column("service_id", ForeignKey("services.id")),
)

class Invoice(db.Model):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float] = mapped_column(Float)
    issue_date: Mapped[date] = mapped_column(Date, default=date.today())

    reservation_id: Mapped[int] = mapped_column(ForeignKey("reservations.id"))
    reservation: Mapped["Reservation"] = relationship(back_populates="invoice")

    services: Mapped[List["Service"]] = relationship(secondary=invoice_service, back_populates="invoices")

    def __repr__(self) -> str:
        return f"Invoice(id={self.id!r}, amount={self.amount!r}, issue_date={self.issue_date!r})"