from app.extensions import db
from app.blueprints.reservation.schemas import ReservationResponseSchema, ReservationListSchema, ReservationRequestSchema
from app.models.user import User
from app.models.room import Room
from app.models.reservation import Reservation

from sqlalchemy import select, and_

class ReservationService:
    
    @staticmethod
    def add_reservation(request):
        try:
            user = User.query.get(request['user'])
            rooms = db.session.query(Room).filter(Room.id.in_(request['room_ids'])).all()
            
            if not user or len(rooms) != len(request['room_ids']):
                return False, "Invalid user or room IDs"

            reservation = Reservation(
                start_date=request['start_date'],
                end_date=request['end_date'],
                reservation_date=request['reservation_date'],
                user=user
            )
            reservation.rooms.extend(rooms)
            db.session.add(reservation)
            db.session.commit()
            
            return True, ReservationResponseSchema().dump(reservation)
        except Exception as ex:
            print(ex)
            return False, "reservation_add() error!"
   
    @staticmethod
    def reservation_list_all():
        reservation = db.session.execute( select(Reservation)).scalars().all()
        return True, ReservationListSchema().dump(reservation, many = True)
    
    @staticmethod
    def serach_reservation_by_room(rid):
        reservations = db.session.execute(
            select(Reservation).filter(Reservation.rooms.any(Room.id == rid))
        ).scalars().all()
        if not reservations:
            return False, "Reservation not found!"
        return True, ReservationListSchema().dump(reservations, many=True)

    @staticmethod
    def serach_reservation_by_id(rid):
        reservation = db.session.execute(select(Reservation).filter(Reservation.id==rid)).scalar_one_or_none()
        if reservation is None:
            return False, "Reservatin not found!"
        return True,ReservationListSchema().dump(reservation)

    @staticmethod
    def serach_reservation_by_user(uid):
        reservation = db.session.execute(select(Reservation).filter(Reservation.user_id==uid)).scalars() 
        if reservation is None:
            return False, "Reservatin not found!"
        return True,ReservationListSchema().dump(reservation, many=True)
    

    @staticmethod
    def update_reservation(rid, request):
        try:
            reservation = db.session.get(Reservation, rid)
            if reservation:
                user = User.query.get(request["user"])
                rooms = db.session.query(Room).filter(Room.id.in_(request['room_ids'])).all()
                
                if not user or len(rooms) != len(request['room_ids']):
                    return False, "Invalid user or room IDs"
                    
                reservation.start_date = request["start_date"]
                reservation.end_date = request["end_date"]
                reservation.reservation_date = request["reservation_date"]
                reservation.user = user
                reservation.rooms = rooms
                reservation.deleted = request["deleted"]
                db.session.commit()
                return True, ReservationResponseSchema().dump(reservation)
            return False, "Reservation not found!"
            
        except Exception as ex:
            print(ex)
            return False, "Reservation_update() error!"

    # @staticmethod
    # def delete_reservation(rid):
    #     try:
    #         reservation = db.session.get(Reservation, rid)
    #         if reservation:
    #             reservation.deleted = 1
    #             db.session.commit()
            
    #     except Exception as ex:
    #         return False, "reservation_delete() error!"
    #     return True, "OK"