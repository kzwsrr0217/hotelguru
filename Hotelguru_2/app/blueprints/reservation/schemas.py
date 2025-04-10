from marshmallow import Schema, fields
from apiflask.fields import String, Email, Nested, Integer, List, Date
from apiflask.validators import Length, OneOf, Email

from app.models.reservation import Reservation
from app.blueprints.user.schemas import UserResponseSchema
from app.models.room import Room
from app.models.room_type import RoomType


class SuccessMessageSchema(Schema):  # teszthez
    message = fields.String()


class SchemaForRoom(Schema):
    number = fields.Integer()


class RoomTypeRequestItem(Schema):
    room_type_id = fields.Integer()
    quantity = fields.Integer()


class ReservationRequestSchema(Schema):
    start_date = fields.Date()
    end_date = fields.Date()
    reservation_date = fields.Date(required=False)
    room_numbers = fields.List(fields.Integer())


"""class ReservationUpdateSchema(Schema):
    start_date = fields.Date()
    end_date = fields.Date()
    reservation_date= fields.Date()
    room_numbers = fields.List(fields.Integer())
    status = fields.String()
"""


class ReservationResponseSchema(Schema):
    start_date = fields.String()
    end_date = fields.String()
    reservation_date = fields.String()
    rooms = fields.List(fields.Nested(SchemaForRoom))
    status = fields.String()


class ReservationListSchema(Schema):
    id = fields.Integer()
    start_date = fields.String()
    end_date = fields.String()
    reservation_date = fields.String()
    rooms = fields.List(fields.Nested(SchemaForRoom))
    status = fields.String()


class ReservationByUserSchema(Schema):
    id = fields.Integer()
    start_date = fields.String()
    end_date = fields.String()
    reservation_date = fields.String()
    rooms = fields.List(fields.Nested(SchemaForRoom))
    status = fields.String()
