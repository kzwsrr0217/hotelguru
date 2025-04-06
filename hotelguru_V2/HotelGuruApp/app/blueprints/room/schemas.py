from marshmallow import Schema, fields
from apiflask.fields import String, Email, Nested, Integer, List, Boolean, Float
from apiflask.validators import Length, OneOf, Email
from app.models.room import Room

class RoomTypeSchema(Schema):
    #id = fields.Integer()
    name = fields.String()

class RoomRequestSchema(Schema):
    number = fields.Integer()
    floor = fields.Integer()
    name = fields.String()
    description = fields.String()
    price = fields.Float()
    is_available = fields.Boolean()
    room_type_id = fields.Integer()

class RoomUpdateSchema(Schema):
    name = fields.String()
    description = fields.String()
    price = fields.Float()
    is_available = fields.Boolean()
    room_type_id = fields.Integer()
    
class RoomResponseSchema(Schema):
    number = fields.Integer()
    floor = fields.Integer()
    name = fields.String()
    description = fields.String()
    price = fields.Float()
    is_available = fields.Boolean()
    room_type_id = fields.Integer()



class AllRoomListSchema(Schema):
    number = fields.Integer()
    floor = fields.Integer()
    name = fields.String()
    price = fields.Float()
    room_type = fields.Nested(RoomTypeSchema)


class RoomSchema(Schema):
    number = fields.Integer()
    floor = fields.Integer()
    name = fields.String()
    description = fields.String()
    price = fields.Float()
    room_type = fields.Nested(RoomTypeSchema)