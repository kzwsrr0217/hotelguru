# Hotelguru_2/app/blueprints/reservation/schemas.py
from marshmallow import Schema, fields # Csak fields kell, a post_dump-ot kivesszük
from apiflask.fields import String, Nested, Integer, List, Date
import datetime # datetime itt nem feltétlenül kell, ha fields.Date()-et használunk
import logging

# --- Egyszerűsített sémák ---
class SchemaForRoom(Schema):
    number = fields.Integer()

class ServiceSimpleSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    price = fields.Float()
# --- /Egyszerűsített sémák ---

class SuccessMessageSchema(Schema):
    message = fields.String()

# --- Fő Sémák ---
class ReservationRequestSchema(Schema): # Bemenethez marad Date a validáció miatt
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    reservation_date = fields.Date(required=False)
    room_numbers = fields.List(fields.Integer(), required=True)

# NINCS ReservationBaseSchema

class ReservationResponseSchema(Schema):
    start_date = fields.Date() # Marad fields.Date()
    end_date = fields.Date()
    reservation_date = fields.Date()
    rooms = fields.List(fields.Nested(SchemaForRoom))
    status = fields.String(attribute="status.name", default=None)

class ReservationListSchema(Schema):
    id = fields.Integer()
    start_date = fields.Date() # Marad fields.Date()
    end_date = fields.Date()
    reservation_date = fields.Date()
    rooms = fields.List(fields.Nested(SchemaForRoom))
    status = fields.String(attribute="status.name", default=None)

class ReservationByUserSchema(Schema):
    id = fields.Integer()
    start_date = fields.Date()       # <<< Vissza fields.Date()-re
    end_date = fields.Date()         # <<< Vissza fields.Date()-re
    reservation_date = fields.Date() # <<< Vissza fields.Date()-re
    rooms = fields.List(fields.Nested(SchemaForRoom))
    status = fields.String(attribute="status.name", default=None)

    # <<< Vissza a legegyszerűbb fields.Nested + attribute megközelítéshez >>>
    invoice_services = fields.Nested(ServiceSimpleSchema, many=True, attribute="invoice.services", dump_default=[])

    # NINCS @post_dump metódus