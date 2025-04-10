from marshmallow import Schema, fields


class InvoiceSchema(Schema):
    id = fields.Integer()
    reservation_id = fields.Integer()
    total_amount = fields.Float()
    issue_date = fields.Date()
    items = fields.List(fields.Dict())  # Pl.: {"room": "101", "price": 15000}
