from marshmallow import Schema, fields
from apiflask.fields import String, Email, Nested, Integer, List
from apiflask.validators import Length, OneOf, Email
from app.models.user import User




class AddressSchema(Schema):
    city= fields.String()
    street= fields.String()
    postalcode = fields.Integer()


class UserRequestSchema(Schema):
        
    name = fields.String()
    email = String(validate=Email())
    password = fields.String(validate=Length(min=6))
    phone = fields.String()
    address = fields.Nested(AddressSchema)


class UserResponseSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    email = fields.String()
    address = fields.Nested(AddressSchema)
    

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
