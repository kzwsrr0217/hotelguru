from marshmallow import Schema, fields
from marshmallow.validate import OneOf
from apiflask.fields import String, Integer, Date, List, Float


class ReservationReceptionistSchema(Schema):
    id = fields.Integer()
    start_date = fields.Date()
    end_date = fields.Date()
    guest_name = fields.String(attribute="user.name")  # Vendég neve a User modellből
    rooms = fields.List(fields.String(attribute="number"))  # Szobaszámok


class ReservationUpdateStatusSchema(Schema):
    status = fields.String(
        required=True, validate=OneOf(["Pending", "Confirmed", "Cancelled"])
    )


class AddServicesSchema(Schema):
    service_ids = List(
        fields.Integer(),
        required=True,
        description="A hozzáadandó szolgáltatások azonosítóinak listája.",
    )


class InvoiceSummarySchema(Schema):
    id = fields.Integer()
    amount = fields.Float(description="A számla frissített végösszege.")
    status = fields.String(
        description="A számla státusza (valószínűleg 'Live')."
    )  # Vagy EnumField, ha van
