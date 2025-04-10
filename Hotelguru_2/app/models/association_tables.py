from app.extensions import db
from sqlalchemy import Column, ForeignKey, Table

invoice_service = db.Table(
    "invoice_service",
    db.metadata,
    Column("invoice_id", ForeignKey("invoices.id"), primary_key=True),
    Column("service_id", ForeignKey("services.id"), primary_key=True),
)

reservation_room = db.Table(
    "reservation_room",
    db.metadata,
    Column("reservation_id", ForeignKey("reservations.id"), primary_key=True),
    Column("room_id", ForeignKey("rooms.id"), primary_key=True),
)
