from marshmallow import Schema, fields
from apiflask.fields import String, Email, Nested, Integer, List, Date
from apiflask.validators import Length, OneOf, Email

from app.models.reservation import Reservation
from app.blueprints.user.schemas import UserResponseSchema
from app.models.room import Room

class UserSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    
class RoomSchema(Schema):
    id = fields.Integer()
    number = fields.Integer()
    floor = fields.Integer()
    name = fields.String()  


class ReservationRequestSchema(Schema):
    start_date = fields.Date()
    end_date = fields.Date()
    reservation_date= fields.Date()
    user = fields.Integer(data_key="user_id") 
    room_ids = fields.List(fields.Integer())
    
class ReservationUpdateSchema(Schema):
    start_date = fields.Date()
    end_date = fields.Date()
    reservation_date= fields.Date()
    user = fields.Integer(data_key="user_id") 
    room_ids = fields.List(fields.Integer())
    deleted = fields.Integer()

class ReservationResponseSchema(Schema):
    start_date = fields.String()
    end_date = fields.String()
    reservation_date = fields.String()
    user = fields.Nested(UserSchema) 
    rooms = fields.List(fields.Nested(RoomSchema))
    

class ReservationListSchema(Schema):
    id = fields.Integer()
    start_date = fields.String()
    end_date = fields.String()
    reservation_date = fields.String()
    user = fields.Nested(UserSchema) 
    rooms = fields.List(fields.Nested(RoomSchema))
    deleted = fields.Integer()
