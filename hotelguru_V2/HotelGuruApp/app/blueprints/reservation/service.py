from platform import android_ver
from app.extensions import db
from app.blueprints.reservation.schemas import ReservationResponseSchema, ReservationListSchema, ReservationRequestSchema, ReservationByUserSchema
from app.models.user import User
from app.models.room import Room
from app.models.reservation import Reservation, StatusEnum

from sqlalchemy import select, and_, or_

class ReservationService:

    @staticmethod
    def add_reservation(request):
        try:
            user = User.query.get(request['user'])
            if not user:
                return False, "Invalid user"
            selected_rooms = []
            for room_number_request in request['room_numbers']:
                rooms = db.session.query(Room).filter(
                    and_(
                        Room.number == room_number_request,
                        Room.is_available == True
                    )
                ).all()
                
                if not rooms:
                    return False, f"Room number {room_number_request} is not available or does not exist"
            
                selected_rooms.extend(rooms)

            reservation = Reservation(
                start_date=request['start_date'],
                end_date=request['end_date'],
                reservation_date=request['reservation_date'],
                user=user
            )
        
            reservation.rooms.extend(selected_rooms)
        
            for room in selected_rooms:
                room.is_available = False
            
            db.session.add(reservation)
            db.session.commit()
        
            return True, ReservationResponseSchema().dump(reservation)
        
        except Exception as ex:
            print(ex)
            db.session.rollback()
            return False, "reservation_add() error!"
    
    @staticmethod
    def reservation_list_all():
        reservations = db.session.execute(select(Reservation)).scalars().all()
        return True,ReservationListSchema().dump(reservations, many=True)

    @staticmethod
    def serach_reservation_by_room(rid):
        reservations = db.session.execute(
            select(Reservation).filter(Reservation.rooms.any(Room.number == rid))
        ).scalars().all()
        if not reservations:
            return False, "Reservation not found!"
        return True,ReservationListSchema().dump(reservations, many=True)

    @staticmethod
    def serach_reservation_by_id(rid):
        reservation = db.session.execute(select(Reservation).filter(Reservation.id==rid)).scalar_one_or_none()
        if reservation is None:
            return False, "Reservation not found!"
        #return True, ReservationService.serialize_reservations(reservation)
        return True,ReservationListSchema().dump(reservation)

    @staticmethod
    def serach_reservation_by_user(uid):
        reservations = db.session.execute(select(Reservation).filter(
            and_(
                Reservation.user_id==uid,
                or_(
                    Reservation.status == "Depending",
                    Reservation.status == "Success"
                )
            )
        )).scalars().all()
        if not reservations:
            return False, "User not found!"
        return True,ReservationByUserSchema().dump(reservations, many=True)

    

    @staticmethod
    def update_reservation(rid, request):
        try:
            reservation = db.session.get(Reservation, rid)
            if reservation:
                rooms = db.session.query(Room).filter(Room.number.in_(request['room_numbers'])).all()
                
                #if not user or 
                if len(rooms) != len(request['room_numbers']):
                    return False, "Invalid user or room numberss"
                    
                reservation.start_date = request["start_date"]
                reservation.end_date = request["end_date"]
                reservation.reservation_date = request["reservation_date"]
                reservation.rooms = rooms
                reservation.status = request["status"]
                db.session.commit()
                return True, ReservationResponseSchema().dump(reservation)
            return False, "Reservation not found!"
            
        except Exception as ex:
            print(ex)
            return False, "Reservation_update() error!"
