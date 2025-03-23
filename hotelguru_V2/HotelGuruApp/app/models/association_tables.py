from app.extensions import db
from sqlalchemy import Column, ForeignKey

invoice_service = db.Table(
    "invoice_service",
    Column("invoice_id", ForeignKey("invoices.id")),
    Column("service_id", ForeignKey("services.id")),
)
