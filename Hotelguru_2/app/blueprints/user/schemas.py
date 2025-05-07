from marshmallow import Schema, fields
from apiflask.fields import String, Email, Nested, Integer, List
from apiflask.validators import Length, OneOf, Email
from app.models.user import User


class AddressSchema(Schema):
    city = fields.String(required=True, description="Város neve")
    street = fields.String(required=True, description="Utca és házszám")
    postalcode = fields.Integer(required=True, description="Irányítószám")


class UserRequestSchema(Schema):
    name = fields.String(required=True, description="Felhasználó teljes neve")
    email = String(
        required=True, validate=Email(), description="Felhasználó email címe (egyedi)"
    )
    password = fields.String(
        required=True, validate=Length(min=6), description="Jelszó (minimum 6 karakter)"
    )
    phone = fields.String(required=True, description="Telefonszám")
    address = fields.Nested(
        AddressSchema, required=True, description="Felhasználó címe"
    )


class UserResponseSchema(Schema):
    id = fields.Integer(dump_only=True, description="Felhasználó egyedi azonosítója")
    name = fields.String(description="Felhasználó teljes neve")
    email = fields.String(description="Felhasználó email címe")
    phone = fields.String(description="Telefonszám") # <<< HOZZÁADVA
    address = fields.Nested(AddressSchema, description="Felhasználó címe")


class UserLoginSchema(Schema):
    email = String(validate=Email())
    password = fields.String()


class RoleSchema(Schema):
    id = fields.Integer()
    name = fields.String()


class UserUpdateSchema(Schema):
    email = String(validate=Email())
    address = fields.Nested(AddressSchema)
    phone_number = fields.String()
    password = fields.String(validate=Length(min=6))


class TokenSchema(Schema):
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)
