from marshmallow import Schema, fields


class RoomAdminSchema(Schema):
    # number = fields.Integer(dump_only=True) # Vagy teljesen távolítsuk el a PUT sémából
    name = fields.String(
        required=False
    )  # Opcionális, ha nem adunk meg nevet, akkor a számot használja
    description = fields.String(
        required=False, allow_none=True
    )  # Opcionális, ha nem adunk meg leírást, akkor None lesz
    price = fields.Float(
        required=False
    )  # Opcionális, ha nem adunk meg árat, akkor None lesz
    is_available = fields.Boolean(
        required=False
    )  # Opcionális, ha nem adunk meg elérhetőséget, akkor None lesz
    room_type_id = fields.Integer(required=False, allow_none=True) # <<< allow_none=True HOZZÁADVA

      # Opcionális, ha nem adunk meg szobatípust, akkor None lesz


class ServiceAdminSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    price = fields.Float()
