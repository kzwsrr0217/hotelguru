from app.extensions import db
from app.blueprints.room.schemas import RoomResponseSchema, RoomRequestSchema, RoomListSchema

#from app.models.room_type import Roomtype
from app.models.room import Room

from sqlalchemy import select, and_

class RoomService:
    
    @staticmethod
    def room_add(request):
        try:
           
            room = Room(**request)
            db.session.add(room)
            db.session.commit()
            
        except Exception as ex:
            print(ex)
            return False, "room_add() error!"
        return True, RoomResponseSchema().dump(room)
    
    @staticmethod
    def room_list_all():
        rooms = db.session.execute( select(Room)).scalars()
        return True, RoomListSchema().dump(rooms, many = True)
    
    @staticmethod
    def room_list_type(rid):
        rooms = db.session.execute(select(Room).filter(Room.room_type_id==rid)).scalars()       
        return True, RoomListSchema().dump(rooms, many = True)

    @staticmethod
    def room_update(rid, request):
        try:
            room = db.session.get(Room, rid)
            if room:
                room.number = request["number"]
                room.floor = request["floor"]
                room.name = request["name"]
                room.description = request["description"]
                room.price = float(request["price"])
                room.is_available = bool(request["is_available"])
                room.room_type_id = int(request["room_type_id"])
                db.session.commit()
            
        except Exception as ex:
            print(ex)
            return False, "room_update() error!"
        return True, RoomResponseSchema().dump(room)

