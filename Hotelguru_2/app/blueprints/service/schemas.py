from marshmallow import Schema, fields
from apiflask.fields import String, Email, Nested, Integer, List, Float
from apiflask.validators import Length, OneOf, Email


class ServiceRequestSchema(Schema):
    name = fields.String()
    description = fields.String()
    price = fields.Float()


class ServiceResponseSchema(Schema):
    name = fields.String()
    description = fields.String()
    price = fields.Float()


class ServiceListSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    description = fields.String()
    price = fields.Float()
    deleted = fields.Integer()


class ServiceUpdateSchema(Schema):
    name = fields.String()
    description = fields.String()
    price = fields.Float()
    deleted = fields.Integer()
