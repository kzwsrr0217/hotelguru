from app.extensions import db
from app.blueprints.room.schemas import (
    RoomResponseSchema,
    RoomRequestSchema,
    RoomSchema,
    AllRoomListSchema,
    RoomAdminListSchema,
)

from app.models.room import Room
from app.models.reservation import Reservation, StatusEnum as ReservationStatusEnum # Importáljuk a foglalást és a státusz enumot
from sqlalchemy import select, and_, not_ # Importáljuk a szükséges SQLAlchemy funkciókat
import logging # Logoláshoz
from datetime import date # Dátum típushoz
from typing import Union
from app.models.association_tables import reservation_room


class RoomService:

    @staticmethod
    def room_add(request):
        try:
            room = Room(**request)
            db.session.add(room)
            db.session.commit()
        except Exception as ex:
            logging.exception(f"Error in room_add: {ex}")  # Javított hibakezelés
            db.session.rollback()
            return False, f"Error adding room: {ex}"
        return True, RoomResponseSchema().dump(room)

    @staticmethod
    def room_list_all():  # Ez marad az ELÉRHETŐ szobák listázására
        try:
            rooms = (
                db.session.execute(
                    select(Room)
                    .filter(Room.is_available.is_(True))
                    .order_by(Room.number)
                )
                .scalars()
                .all()
            )
            return True, AllRoomListSchema().dump(rooms, many=True)
        except Exception as e:
            logging.exception(f"Error listing available rooms: {e}")
            return False, "Error retrieving available room list"

    @staticmethod
    def get_room_by_number(room_number):  # Paraméter átnevezve
        """Lekérdez egy ELÉRHETŐ szobát a SZÁMA alapján."""
        try:
            room = db.session.execute(
                select(Room).filter(
                    and_(
                        Room.number == room_number,  # Logika már számot használt
                        Room.is_available.is_(True),
                    )
                )
            ).scalar_one_or_none()
            if room is None:
                return False, "Available room with specified number not found"
            return True, RoomSchema().dump(room)
        except Exception as e:
            logging.exception(f"Error getting room by number {room_number}: {e}")
            return False, "Error retrieving room details"

    # lehet felesleges, mert a room_update már megvan az adminban
    @staticmethod
    def room_update(rid, request):  # Ez az ID alapján módosít
        try:
            room = db.session.get(Room, rid)  # Itt ID-t használ
            if room:
                room.name = request.get(
                    "name", room.name
                )  # Használj .get()-et a biztonság kedvéért
                room.description = request.get("description", room.description)
                room.price = float(request.get("price", room.price))
                room.is_available = bool(request.get("is_available", room.is_available))
                room.room_type_id = int(request.get("room_type_id", room.room_type_id))
                db.session.commit()
                return True, RoomResponseSchema().dump(room)
            else:
                return False, "Room not found!"

        except Exception as ex:
            logging.exception(f"Error updating room {rid}: {ex}")
            db.session.rollback()
            return False, f"Error updating room: {ex}"

    @staticmethod
    def list_all_rooms_admin():
        """Lekérdezi az összes szobát adminisztrációs célra."""
        try:
            # Lekérdezzük az összes szobát, szűrés nélkül, szám szerint rendezve
            all_rooms = (
                db.session.execute(select(Room).order_by(Room.number)).scalars().all()
            )
            # Az új admin sémát használjuk a válaszhoz
            return True, RoomAdminListSchema().dump(all_rooms, many=True)
        except Exception as e:
            logging.exception(f"Error listing all rooms for admin: {e}")
            return False, "Error retrieving full room list"
    @staticmethod
    def find_available_rooms(start_date: Union[date, None] = None, end_date: Union[date, None] = None):
        try:
            logging.info(f"Attempting to find available rooms. Start: {start_date}, End: {end_date}") # <<< Log
            base_query = select(Room).filter(Room.is_available == True)

            if start_date and end_date:
                if start_date >= end_date:
                     logging.warning("Start date is not before end date.") # <<< Log
                     return False, "A kezdő dátumnak korábban kell lennie, mint a vég dátum."

                logging.info(f"Filtering by date range: {start_date} to {end_date}") # <<< Log

                conflicting_statuses = [
                    ReservationStatusEnum.Depending,
                    ReservationStatusEnum.Success,
                    ReservationStatusEnum.CheckedIn,
                ]
                logging.debug(f"Conflicting reservation statuses: {[s.name for s in conflicting_statuses]}") # <<< Log

                # Összeállítjuk az allekérdezést
                conflicting_room_ids_subquery_stmt = ( # <<< Elnevezzük a statementet
                    select(reservation_room.c.room_id)
                    .join(Reservation, reservation_room.c.reservation_id == Reservation.id)
                    .filter(
                        Reservation.status.in_(conflicting_statuses),
                        and_(
                            Reservation.start_date < end_date,
                            Reservation.end_date > start_date
                        )
                    )
                    .distinct()
                )
                # Lefuttatjuk külön az allekérdezést logoláshoz
                conflicting_ids_result = db.session.execute(conflicting_room_ids_subquery_stmt).scalars().all()
                logging.info(f"Conflicting room IDs found by subquery: {conflicting_ids_result}") # <<< LOGOLJUK A FOGLALT SZOBÁK ID-IT!

                # Létrehozzuk a scalar subquery-t a fő lekérdezéshez
                conflicting_room_ids_subquery = conflicting_room_ids_subquery_stmt.scalar_subquery()

                # Fő lekérdezés szűréssel
                query = base_query.filter(not_(Room.id.in_(conflicting_room_ids_subquery)))
                logging.debug("Applied NOT IN filter based on subquery.") # <<< Log

            else:
                logging.info("No date range specified, using base query for generally available rooms.") # <<< Log
                query = base_query

            query = query.order_by(Room.number)

            # Logoljuk a végleges SQL lekérdezést (opcionális, de hasznos lehet)
            # Vigyázat: Ez a pontos szintaxis függhet a DB driver-től és SQLAlchemy verziótól
            try:
                from sqlalchemy.dialects import mysql
                logging.debug(f"Final SQL Query (approx): {query.compile(dialect=mysql.dialect(), compile_kwargs={'literal_binds': True})}")
            except Exception as compile_err:
                logging.warning(f"Could not compile query for logging: {compile_err}")


            available_rooms = db.session.execute(query).scalars().all()
            logging.info(f"Found {len(available_rooms)} available rooms after filtering.") # <<< Log

            return True, AllRoomListSchema(many=True).dump(available_rooms)

        except Exception as e:
            logging.exception(f"Error finding available rooms: {e}")
            db.session.rollback()
            return False, "Hiba történt az elérhető szobák keresése közben."
