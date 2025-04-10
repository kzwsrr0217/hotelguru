from marshmallow import Schema, fields
from apiflask.fields import String, Email, Nested, Integer, List, Boolean, Float, Date 
from apiflask.validators import Length, OneOf, Email
from app.models.room import Room


class RoomTypeSchema(Schema):
    # id = fields.Integer()
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
    id = fields.Integer()
    number = fields.Integer()
    floor = fields.Integer()
    name = fields.String()
    price = fields.Float()
    room_type = fields.Nested(RoomTypeSchema)


class RoomSchema(Schema):
    id = fields.Integer()
    number = fields.Integer()
    floor = fields.Integer()
    name = fields.String()
    description = fields.String()
    price = fields.Float()
    room_type = fields.Nested(RoomTypeSchema)


class RoomAdminListSchema(Schema):
    id = fields.Integer()  # Szoba adatbázis ID
    number = fields.Integer()
    floor = fields.Integer()
    name = fields.String()
    price = fields.Float()
    room_type = fields.Nested(RoomTypeSchema)  # Szoba típusa
    is_available = fields.Boolean()  # Elérhetőségi státusz

class RoomAvailabilityQuerySchema(Schema):
    start_date = fields.Date(required=False, description="Az elérhetőség keresésének kezdő dátuma (YYYY-MM-DD)")
    end_date = fields.Date(required=False, description="Az elérhetőség keresésének záró dátuma (YYYY-MM-DD)")