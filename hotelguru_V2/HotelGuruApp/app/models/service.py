from __future__ import annotations

from typing import List, Optional
from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer, Float

from app.models.association_tables import invoice_service


class Service(db.Model):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(200))
    price: Mapped[float] = mapped_column(Float)
    deleted : Mapped[int] = mapped_column(default = 0)
    

    invoices: Mapped[List["Invoice"]] = relationship(secondary=invoice_service, back_populates="services")

    def __repr__(self) -> str:
        return f"Service(id={self.id!r}, name={self.name!s}, description={self.description!s} , price={self.price!r})"
