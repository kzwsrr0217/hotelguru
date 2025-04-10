from app.extensions import db
from app.models.room import Room  # <<< Room importálása
from app.models.room_type import RoomType
import logging
from sqlalchemy.exc import IntegrityError # <<< Import az egyediségi hibákhoz

# Importáljuk a request sémát a room blueprintből
from app.blueprints.room.schemas import RoomRequestSchema # <<< Lehet, hogy ez nem a legjobb hely, de most használjuk innen


class AdminService:
    @staticmethod
    def get_all_rooms():
        # Példa: lekérdezi az összes szobát az adatbázisból
        try:
            rooms = Room.query.all()
            return True, rooms
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update_room(room_id, data):
        """Frissíti egy szoba adatait az adatbázisban ID alapján."""
        try:
            room = db.session.get(Room, room_id)  # get() használata ID alapú lekéréshez
            if not room:
                return False, "Szoba nem található"

            # Mezők frissítése, ha szerepelnek a 'data'-ban
            # A szobaszámot (number) általában nem módosítjuk
            if "name" in data:
                room.name = data["name"]
            if "description" in data:
                # Lehetővé teszi a description törlését is None-nal
                room.description = data["description"]
            if "price" in data:
                try:
                    room.price = float(data["price"])
                except (ValueError, TypeError):
                    return False, "Érvénytelen ár formátum."
            if "is_available" in data:
                room.is_available = bool(data["is_available"])
            if "room_type_id" in data:
                received_room_type_id = data["room_type_id"]

                # <<< A LÉNYEGI VÁLTOZTATÁS ITT KEZDŐDIK >>>
                # Csak akkor foglalkozunk vele, ha nem None
                if received_room_type_id is not None:
                    # Ellenőrzés és beállítás csak akkor, ha van konkrét ID
                    room_type_exists = (
                        db.session.query(RoomType.id)
                        .filter_by(id=received_room_type_id)
                        .first()
                    )
                    if not room_type_exists:
                        # Ha az ID nem None, de nem létezik, az hiba
                        return False, f"Érvénytelen szobatípus ID: {received_room_type_id}"
                    try:
                        room.room_type_id = int(received_room_type_id)
                    except (ValueError, TypeError):
                        # Ez elvileg nem fordulhat elő, ha a exists check jó volt
                        return False, "Érvénytelen szobatípus ID formátum."
                # Ha received_room_type_id == None, akkor nem csinálunk semmit,
                # a szoba room_type_id mezője változatlan marad.
            db.session.commit()
            logging.info(f"Room {room_id} updated successfully by admin.")
            return True, room  # Visszaadjuk a frissített objektumot
        except Exception as e:
            db.session.rollback()
            logging.exception(f"Error updating room {room_id}: {e}")
            return False, "Szerverhiba történt a szoba frissítése közben."

    @staticmethod
    def delete_room(room_id):
        """Töröl egy szobát az adatbázisból ID alapján."""
        try:
            # Modern lekérdezés ID alapján
            room = db.session.get(Room, room_id)
            if not room:
                logging.warning(f"Attempted to delete non-existent room with ID: {room_id}")
                return False, "Szoba nem található"

            logging.info(f"Deleting room {room_id} (Number: {room.number})")
            db.session.delete(room)
            db.session.commit() # Véglegesítés
            return True, "Szoba sikeresen törölve"

        except Exception as e:
            db.session.rollback() # <<< Rollback hozzáadva hiba esetére!
            logging.exception(f"Error deleting room {room_id}: {e}")
            # Adjunk vissza egy általánosabb hibaüzenetet
            return False, "Szerverhiba történt a szoba törlése közben."
    @staticmethod
    def add_room(data: dict):
        """
        Új szobát ad hozzá az adatbázishoz.
        A 'data' dictionary-nek a RoomRequestSchema által definiált mezőket kell tartalmaznia.
        """
        # Kötelező mezők ellenőrzése (bár a séma is ellenőrzi)
        required_fields = ['number', 'floor', 'name', 'price', 'room_type_id']
        if not all(field in data for field in required_fields):
            missing = [field for field in required_fields if field not in data]
            return False, f"Hiányzó kötelező mezők: {', '.join(missing)}"

        # Szobaszám egyediségének ellenőrzése
        existing_room = db.session.execute(
            db.select(Room).filter_by(number=data['number'])
        ).scalar_one_or_none()
        if existing_room:
            return False, f"A(z) {data['number']} szobaszám már létezik."

        # Szobatípus ID érvényességének ellenőrzése
        room_type_exists = db.session.execute(
            db.select(RoomType.id).filter_by(id=data['room_type_id'])
        ).scalar_one_or_none()
        if not room_type_exists:
             return False, f"Érvénytelen szobatípus ID: {data['room_type_id']}"

        try:
            # Új Room objektum létrehozása a kapott adatokból
            # A RoomRequestSchema mezői: number, floor, name, description, price, is_available, room_type_id
            new_room = Room(
                number=int(data['number']),
                floor=int(data['floor']),
                name=data['name'],
                description=data.get('description'), # Description nem kötelező a sémában? Ellenőrizd! Ha igen, data['description']
                price=float(data['price']),
                # Az is_available alapértelmezetten True a modellben, de felülírhatjuk, ha jön a requestben
                is_available=data.get('is_available', True),
                room_type_id=int(data['room_type_id'])
            )

            db.session.add(new_room)
            db.session.commit()
            logging.info(f"New room created successfully: Number {new_room.number}, ID {new_room.id}")

            # Visszaadhatjuk a létrehozott szoba adatait (pl. RoomAdminSchema-val)
            from .schemas import RoomAdminSchema # Helyi import, vagy tedd felülre
            return True, RoomAdminSchema().dump(new_room)

        except IntegrityError as e:
             db.session.rollback()
             # Ez akkor jöhet elő, ha pl. a szobaszám mégis foglalt volt (párhuzamos kérés)
             logging.error(f"Integrity error while adding room: {e}")
             return False, "Adatbázis hiba történt (pl. szobaszám már létezik)."
        except (ValueError, TypeError) as e:
            db.session.rollback()
            logging.error(f"Data type error while adding room: {e}")
            return False, f"Érvénytelen adattípus: {e}"
        except Exception as e:
            db.session.rollback()
            logging.exception(f"Unexpected error adding room: {e}")
            return False, "Váratlan szerverhiba történt a szoba hozzáadása közben."