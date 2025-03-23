from app.extensions import db, Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, Integer
from sqlalchemy import ForeignKey, Column, Table
from typing import List, Optional
from app.models.role import Role  # Import the Role class
from app.models.address import Address  # Import the Address class
from app.models.reservation import Reservation  # Import the Reservation class
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import Schema, fields



UserRole = Table(
    "userroles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("role_id", ForeignKey("roles.id"))
)


class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    email: Mapped[Optional[str]]
    password: Mapped[str] = mapped_column(String(30))
    phone : Mapped[str] = mapped_column(String(30))
    
    roles: Mapped[List["Role"]] = relationship(secondary=UserRole, back_populates="users")
   
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))
    address : Mapped["Address"] = relationship(back_populates="user", lazy=True)

    reservations: Mapped[List["Reservation"]] = relationship(back_populates="user")
        
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!s}, email={self.email!r})"
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

# class UserSchemaResponse(Schema):
#     id = fields.Integer()
#     name = fields.String()
#     email = fields.String()
