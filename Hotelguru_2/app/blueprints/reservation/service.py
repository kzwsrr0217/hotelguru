from app.extensions import db
from typing import Union  # Union importálása a type hinthez
from app.blueprints.reservation.schemas import (
    ReservationResponseSchema,
    ReservationListSchema,
    ReservationByUserSchema,
)  # RequestSchema itt nem kell, mert a route kezeli
from app.models.user import User  # User modell importálása
from app.models.room import Room  # Room modell importálása
from app.models.reservation import (
    Reservation,
    StatusEnum,
)  # Reservation és StatusEnum modellek importálása
from sqlalchemy import select, and_, or_, exists
import logging
from datetime import date, datetime, timedelta

MIN_CANCELLATION_DAYS = 2  # Minimum 2 nappal a foglalás előtt lehessen lemondani


class ReservationService:

    @staticmethod
    def _check_for_overlaps(
        room_id: int,
        start_date: date,
        end_date: date,
        exclude_reservation_id: int = None,
    ) -> bool:
        """
        Ellenőrzi, hogy van-e átfedő foglalás egy adott szobára és időszakra,
        opcionálisan kizárva egy adott foglalást (módosításkor hasznos).
        """
        try:
            relevant_statuses = [
                StatusEnum.Depending,
                StatusEnum.Success,
                StatusEnum.CheckedIn,
            ]
            query = (
                select(Reservation)
                .join(Reservation.rooms)
                .filter(
                    Room.id == room_id,
                    Reservation.status.in_(relevant_statuses),
                    Reservation.start_date < end_date,
                    Reservation.end_date > start_date,
                )
            )
            # Ha meg van adva kizárandó ID (módosításkor), adjuk hozzá a szűréshez
            if exclude_reservation_id is not None:
                query = query.filter(Reservation.id != exclude_reservation_id)

            # Optimalizáció: elég egyet találni
            overlapping_reservation = (
                db.session.execute(query.limit(1)).scalars().first()
            )

            if overlapping_reservation:
                logging.warning(
                    f"Overlap detected for Room ID {room_id} on dates {start_date}-{end_date}. "
                    f"Conflicting Res ID: {overlapping_reservation.id}"
                    f"{f' (Excluding Res ID: {exclude_reservation_id})' if exclude_reservation_id else ''}"
                )
                return True  # Van átfedés
            else:
                return False  # Nincs átfedés
        except Exception as e:
            logging.exception(f"Error during overlap check for Room ID {room_id}: {e}")
            return True  # Hiba esetén biztonságosabb az átfedést jelezni

    @staticmethod
    def add_reservation(user_id_from_token: int, request_data: dict):
        """
        Új foglalás hozzáadása dátumvalidációval és központi ütközés-ellenőrzéssel.
        Feltételezi, hogy request_data már validálva van a ReservationRequestSchema által.
        """
        try:
            # 1. Alapvető kulcsok meglétének ellenőrzése (bár a séma ezt már megtehette)
            required_keys = ["start_date", "end_date", "room_numbers"]
            if not all(key in request_data for key in required_keys):
                missing_keys = [key for key in required_keys if key not in request_data]
                return False, f"Hiányzó adatok a kérésben: {', '.join(missing_keys)}"

            if not request_data.get("room_numbers"):
                return False, "Legalább egy szobaszámot meg kell adni."

            # 2. Felhasználó lekérdezése
            user = db.session.get(User, user_id_from_token)
            if not user:
                logging.warning(
                    f"User not found with ID from token: {user_id_from_token}"
                )
                return False, "Hiba: A megadott felhasználó nem található."

            # 3. Dátumok átvétele és validálása (feltételezve, hogy már 'date' objektumok)
            try:
                start_date = request_data["start_date"]
                end_date = request_data["end_date"]
                reservation_date_input = request_data.get("reservation_date")

                if reservation_date_input is None:
                    reservation_date = date.today()
                else:
                    reservation_date = reservation_date_input

                # Típusellenőrzés (biztonsági)
                if not all(
                    isinstance(d, date)
                    for d in [start_date, end_date, reservation_date]
                ):
                    logging.error(
                        f"Váratlan típusok a dátumokhoz: start={type(start_date)}, end={type(end_date)}, reservation={type(reservation_date)}"
                    )
                    raise TypeError(
                        "Belső hiba: Nem megfelelő típusú dátumadatok érkeztek."
                    )

                # Dátum logika validálása
                if start_date >= end_date:
                    return (
                        False,
                        "Hiba: A kezdő dátumnak korábban kell lennie, mint a befejező dátum.",
                    )
                if start_date < date.today():
                    return (
                        False,
                        "Hiba: Foglalás csak a mai naptól kezdődően lehetséges.",
                    )

            except KeyError as ke:
                logging.error(f"Hiányzó kötelező dátumkulcs a request_data-ban: {ke}")
                return False, f"Hiányzó kötelező mező a kérésben: {ke}"
            except TypeError as te:
                logging.error(f"Típushiba a dátumfeldolgozás során (service): {te}")
                return False, "Belső szerverhiba a dátumok feldolgozásakor."

            # 4. Kért szobák lekérdezése és validálása
            requested_room_numbers = request_data["room_numbers"]
            selected_rooms_query = select(Room).filter(
                Room.number.in_(requested_room_numbers)
            )
            selected_rooms = db.session.execute(selected_rooms_query).scalars().all()

            found_room_numbers = {room.number for room in selected_rooms}
            # Összehasonlításhoz érdemes lehet mindkét oldalt stringgé vagy int-té alakítani
            missing_room_numbers = set(map(int, requested_room_numbers)) - set(
                map(int, found_room_numbers)
            )
            if missing_room_numbers:
                return (
                    False,
                    f"Hiba: A következő szobaszám(ok) nem léteznek: {', '.join(map(str, missing_room_numbers))}",
                )

            if not selected_rooms:
                return False, "Hiba: Egyetlen érvényes szoba sem található a kérésben."

            # 5. Ütközés-ellenőrzés (Központosított lekérdezés)
            selected_room_ids = [room.id for room in selected_rooms]
            relevant_statuses_for_overlap = [
                StatusEnum.Depending,
                StatusEnum.Success,
                StatusEnum.CheckedIn,
            ]

            overlap_subquery = (
                exists()
                .where(
                    Reservation.rooms.any(Room.id.in_(selected_room_ids)),
                    and_(
                        Reservation.start_date < end_date,
                        Reservation.end_date > start_date,
                    ),
                    Reservation.status.in_(relevant_statuses_for_overlap),
                )
                .select_from(Reservation)
            )

            has_overlap = db.session.query(overlap_subquery).scalar()

            if has_overlap:
                start_date_str = start_date.strftime("%Y-%m-%d")
                end_date_str = end_date.strftime("%Y-%m-%d")
                return False, (
                    f"Konfliktus: Legalább egy kiválasztott szoba "
                    f"({', '.join(str(n) for n in found_room_numbers)}) már foglalt a kért "
                    f"időszak ({start_date_str} - {end_date_str}) "
                    f"egy részére vagy egészére."
                )

            # 6. Foglalás objektum létrehozása
            reservation = Reservation(
                start_date=start_date,
                end_date=end_date,
                reservation_date=reservation_date,
                user_id=user.id,
                status=StatusEnum.Depending,
            )

            # 7. Szobák hozzárendelése
            reservation.rooms.extend(selected_rooms)

            # 8. Mentés
            db.session.add(reservation)
            db.session.commit()

            logging.info(
                f"Foglalás sikeresen létrehozva (ID: {reservation.id}) a felhasználónak: {user.id}"
            )

            # 9. Sikeres válasz
            schema = ReservationResponseSchema()
            return True, schema.dump(reservation)

        # Külső hibakezelés
        except Exception as ex:
            db.session.rollback()
            logging.exception(
                f"Váratlan hiba történt a foglalás létrehozása közben (User ID: {user_id_from_token}): {ex}"
            )
            return (
                False,
                "Szerverhiba történt a foglalás feldolgozása közben. Kérjük, próbálja újra később.",
            )

    @staticmethod
    def reservation_list_all():
        """Listázza az összes foglalást."""
        try:
            reservations = db.session.execute(select(Reservation)).scalars().all()
            return True, ReservationListSchema(many=True).dump(reservations)
        except Exception as e:
            logging.exception(f"Error listing all reservations: {e}")
            return False, "Hiba a foglalások listázása közben."

    @staticmethod
    def serach_reservation_by_room(room_number: int):
        """Adott szobaszámhoz tartozó foglalások listázása."""
        try:
            reservations_query = select(Reservation).filter(
                Reservation.rooms.any(Room.number == room_number)
            )
            reservations = db.session.execute(reservations_query).scalars().all()
            return True, ReservationListSchema(many=True).dump(
                reservations
            )  # Üres lista, ha nincs találat
        except Exception as e:
            logging.exception(
                f"Error searching reservations by room number {room_number}: {e}"
            )
            return False, "Hiba a szobaszám alapján történő keresés közben."

    @staticmethod
    def serach_reservation_by_id(rid: int):
        """Foglalás keresése azonosító alapján."""
        try:
            reservation = db.session.get(Reservation, rid)
            if reservation is None:
                return False, "A megadott azonosítóval nem található foglalás."
            return True, ReservationListSchema().dump(reservation)
        except Exception as e:
            logging.exception(f"Error searching reservation by ID {rid}: {e}")
            return False, "Hiba az azonosító alapján történő keresés közben."

    @staticmethod
    def serach_reservation_by_user(uid: int):
        """Adott felhasználó aktív foglalásainak listázása."""
        try:
            # User létezésének ellenőrzése (opcionális)
            # user_exists = db.session.query(exists().where(User.id == uid)).scalar()
            # if not user_exists:
            #     return False, "Felhasználó nem található."

            # Következetesen Enum használata a státuszokra
            relevant_statuses = [
                StatusEnum.Depending,
                StatusEnum.Success,
                StatusEnum.CheckedIn,
            ]
            reservations_query = select(Reservation).filter(
                Reservation.user_id == uid, Reservation.status.in_(relevant_statuses)
            )
            reservations = db.session.execute(reservations_query).scalars().all()
            return True, ReservationByUserSchema(many=True).dump(reservations)
        except Exception as e:
            logging.exception(f"Error searching reservations by user ID {uid}: {e}")
            return False, "Hiba a felhasználó foglalásainak keresése közben."

    @staticmethod
    def confirm_reservation(reservation_id: int):
        """Visszaigazol egy 'Depending' státuszú foglalást 'Success'-re ütközésvizsgálattal."""
        try:
            reservation = db.session.get(Reservation, reservation_id)
            if not reservation:
                return False, "Foglalás nem található."

            if reservation.status != StatusEnum.Depending:
                return (
                    False,
                    f"Visszaigazolás sikertelen: A foglalás státusza '{reservation.status.name}', csak 'Depending' státuszú igazolható vissza.",
                )

            if not reservation.rooms:
                logging.warning(
                    f"Cannot confirm reservation {reservation_id}: No rooms associated."
                )
                return (
                    False,
                    "Visszaigazolás sikertelen: Nincsenek szobák a foglaláshoz rendelve.",
                )

            # Ütközés ellenőrzés a visszaigazolás pillanatában, saját maga kizárásával
            has_overlap = False
            conflicting_room_numbers = []
            for room in reservation.rooms:
                if ReservationService._check_for_overlaps(
                    room.id,
                    reservation.start_date,
                    reservation.end_date,
                    exclude_reservation_id=reservation_id,
                ):
                    has_overlap = True
                    conflicting_room_numbers.append(str(room.number))
                    # Lehetne itt 'break', ha elég egy ütközést találni

            if has_overlap:
                return False, (
                    f"Visszaigazolás sikertelen: Ütközés észlelve a foglalás időszakában "
                    f"({reservation.start_date.strftime('%Y-%m-%d')} - {reservation.end_date.strftime('%Y-%m-%d')}) "
                    f"a következő szobá(k)nál: {', '.join(conflicting_room_numbers)}. "
                    f"Előfordulhat, hogy időközben másik foglalás lett visszaigazolva."
                )

            # Státusz váltás Success-re
            reservation.status = StatusEnum.Success
            db.session.commit()
            logging.info(f"Reservation {reservation_id} confirmed successfully.")
            return True, "Foglalás sikeresen visszaigazolva."

        except Exception as ex:
            db.session.rollback()
            logging.exception(f"Error confirming reservation {reservation_id}: {ex}")
            return False, "Szerverhiba történt a visszaigazolás során."

    @staticmethod
    def update_reservation(rid: int, request_data: dict):
        """
        Foglalás módosítása ütközésvizsgálattal.
        FIGYELEM: Ez a verzió feltételezi, hogy a request_data tartalmazhat stringeket is,
        és nem feltétlenül esett át előzetes schema validáción erre a célra.
        Egy dedikált ReservationUpdateSchema használata javasolt a route szintjén!
        """
        try:
            reservation = db.session.get(Reservation, rid)
            if not reservation:
                return False, "Foglalás nem található!"

            # --- Módosítandó adatok előkészítése és validálása ---
            new_start_date = reservation.start_date
            new_end_date = reservation.end_date
            new_reservation_date = reservation.reservation_date
            new_status = reservation.status
            selected_rooms = list(reservation.rooms)  # Kiindulunk a meglévő szobákból

            # Dátumok feldolgozása (ha vannak a requestben)
            try:
                if "start_date" in request_data:
                    start_date_input = request_data["start_date"]
                    if isinstance(start_date_input, date):
                        new_start_date = start_date_input
                    elif isinstance(start_date_input, str):
                        new_start_date = datetime.strptime(
                            start_date_input, "%Y-%m-%d"
                        ).date()
                    else:
                        raise TypeError("Érvénytelen start_date típus.")
                # Ugyanez end_date-re...
                if "end_date" in request_data:
                    end_date_input = request_data["end_date"]
                    if isinstance(end_date_input, date):
                        new_end_date = end_date_input
                    elif isinstance(end_date_input, str):
                        new_end_date = datetime.strptime(
                            end_date_input, "%Y-%m-%d"
                        ).date()
                    else:
                        raise TypeError("Érvénytelen end_date típus.")
                # Ugyanez reservation_date-re...
                if "reservation_date" in request_data:
                    res_date_input = request_data["reservation_date"]
                    if res_date_input is None:  # Explicit None kezelése
                        new_reservation_date = date.today()  # Vagy más default logika
                    elif isinstance(res_date_input, date):
                        new_reservation_date = res_date_input
                    elif isinstance(res_date_input, str):
                        new_reservation_date = datetime.strptime(
                            res_date_input, "%Y-%m-%d"
                        ).date()
                    else:
                        raise TypeError("Érvénytelen reservation_date típus.")

                # Dátum logika ellenőrzése a potenciálisan új dátumokkal
                if new_start_date >= new_end_date:
                    return (
                        False,
                        "Hiba: A kezdő dátumnak korábban kell lennie, mint a befejező dátum.",
                    )
                # Múltbeli dátum ellenőrzése (ha szükséges)
                # if new_start_date < date.today(): ...

            except (ValueError, TypeError) as e:
                logging.error(f"Hiba a dátumok feldolgozásakor (update): {e}")
                return False, f"Érvénytelen dátum formátum vagy típus a kérésben: {e}"

            # Státusz feldolgozása (ha van a requestben)
            if "status" in request_data:
                try:
                    status_input = request_data["status"]
                    if isinstance(status_input, StatusEnum):
                        new_status = status_input
                    elif isinstance(status_input, str):
                        # Próbáljuk megkeresni az Enum tagot a string alapján
                        new_status = StatusEnum[
                            status_input
                        ]  # Ez KeyError-t dob, ha nincs ilyen tag
                    else:
                        raise TypeError("Érvénytelen status típus.")
                except (KeyError, TypeError) as e:
                    logging.error(f"Hiba a státusz feldolgozásakor (update): {e}")
                    valid_statuses = [s.name for s in StatusEnum]
                    return (
                        False,
                        f"Érvénytelen státusz érték. Lehetséges értékek: {', '.join(valid_statuses)}",
                    )

            # Szobák feldolgozása (ha vannak a requestben)
            if "room_numbers" in request_data:
                requested_room_numbers = request_data["room_numbers"]
                if not requested_room_numbers:
                    return (
                        False,
                        "Legalább egy szobaszámot meg kell adni a módosításhoz.",
                    )

                rooms_query = select(Room).filter(
                    Room.number.in_(requested_room_numbers)
                )
                new_selected_rooms = db.session.execute(rooms_query).scalars().all()

                if len(new_selected_rooms) != len(requested_room_numbers):
                    found_nums = {r.number for r in new_selected_rooms}
                    missing_nums = set(map(int, requested_room_numbers)) - set(
                        map(int, found_nums)
                    )
                    return (
                        False,
                        f"Érvénytelen szobaszám(ok) a módosításban: {', '.join(map(str, missing_nums))}",
                    )
                # Ha a szobalista valid, ezt fogjuk használni
                selected_rooms = new_selected_rooms
            # Ha nem volt room_numbers a requestben, a 'selected_rooms' a foglalás eredeti szobáit tartalmazza

            # --- Ütközésvizsgálat a MÓDOSÍTOTT adatokkal ---
            new_room_ids = [room.id for room in selected_rooms]
            # Használjuk ugyanazt a központi lekérdezést, mint az add_reservation, de zárjuk ki önmagát
            relevant_statuses_for_overlap = [
                StatusEnum.Depending,
                StatusEnum.Success,
                StatusEnum.CheckedIn,
            ]
            overlap_subquery = (
                exists()
                .where(
                    Reservation.rooms.any(Room.id.in_(new_room_ids)),
                    and_(
                        Reservation.start_date < new_end_date,  # Új dátumok!
                        Reservation.end_date > new_start_date,  # Új dátumok!
                    ),
                    Reservation.status.in_(relevant_statuses_for_overlap),
                    Reservation.id != rid,  # Zárjuk ki önmagát!
                )
                .select_from(Reservation)
            )

            has_overlap = db.session.query(overlap_subquery).scalar()

            if has_overlap:
                start_str = new_start_date.strftime("%Y-%m-%d")
                end_str = new_end_date.strftime("%Y-%m-%d")
                room_nums_str = ", ".join(str(r.number) for r in selected_rooms)
                return False, (
                    f"Módosítás sikertelen: Ütközés észlelve a kért időszakban "
                    f"({start_str} - {end_str}) a következő szobá(k)ra: {room_nums_str}."
                )

            # --- Módosítások alkalmazása, ha minden rendben ---
            reservation.start_date = new_start_date
            reservation.end_date = new_end_date
            reservation.reservation_date = new_reservation_date
            reservation.status = new_status
            reservation.rooms = (
                selected_rooms  # SQLAlchemy kezeli a many-to-many kapcsolat frissítését
            )

            db.session.commit()
            logging.info(f"Reservation {rid} updated successfully.")
            return True, ReservationResponseSchema().dump(reservation)

        except Exception as ex:
            db.session.rollback()
            logging.exception(f"Error updating reservation {rid}: {ex}")
            return False, f"Hiba történt a(z) {rid} foglalás módosítása közben."

    @staticmethod
    def cancel_reservation(reservation_id: int, user_id: int):
        """Lemond egy foglalást a szabályok és jogosultságok alapján."""
        try:
            reservation = db.session.get(Reservation, reservation_id)
            if not reservation:
                return False, "Foglalás nem található."

            user = db.session.get(User, user_id)
            if not user:
                logging.error(
                    f"User not found during cancellation attempt: User ID {user_id} for Res ID {reservation_id}"
                )
                return False, "Felhasználó nem található."

            # Jogosultság ellenőrzés
            is_admin_or_receptionist = any(role.name in ["Administrator", "Receptionist"] for role in user.roles)
            if reservation.user_id != user_id and not is_admin_or_receptionist:
                logging.warning(...)
                return False, "Tiltott: ..."


            # Lemondási szabályok ellenőrzése
            can_cancel = False
            cancel_reason = ""

            if reservation.status in [StatusEnum.Depending, StatusEnum.Success]:
                if reservation.start_date >= date.today():
                    if (
                        reservation.start_date - date.today()
                    ).days >= MIN_CANCELLATION_DAYS:
                        can_cancel = True
                    else:
                        cancel_reason = f"A foglalást legalább {MIN_CANCELLATION_DAYS} nappal az érkezés előtt lehet lemondani."
                elif (
                    not is_admin_or_receptionist
                ):  # Már tart vagy múltbeli, és nem admin/recepciós
                    cancel_reason = (
                        "A már folyamatban lévő vagy múltbeli foglalás nem mondható le."
                    )
                else:  # Admin/Recepciós lemondhatja
                    can_cancel = True
            else:  # Státusz nem megfelelő
                cancel_reason = f"A foglalás nem mondható le '{reservation.status.name}' státusszal."

            if not can_cancel:
                return False, f"Lemondás sikertelen: {cancel_reason}"

            # Lemondás végrehajtása
            reservation.status = StatusEnum.Canceled

            # FIGYELEM: Az 'is_available' flag használata itt egyszerűsítés.
            # A valós elérhetőséget az ütközésvizsgálati logikának kellene kezelnie
            # más foglalások lekérdezésekor. Ennek a flagnek a direkt állítása félrevezető lehet.
            # for room in reservation.rooms:
            #     room.is_available = True # <<< Ezt a sort érdemes lehet eltávolítani/átgondolni

            db.session.commit()
            user_role_names = [r.name for r in user.roles]
            logging.info(
            f"Reservation {reservation_id} cancelled successfully by user {user_id} (Roles: {user_role_names})."
    )
            return True, "Foglalás sikeresen lemondva."

        except Exception as ex:
            db.session.rollback()
            logging.exception(
                f"Error cancelling reservation {reservation_id} by user {user_id}: {ex}"
            )
            return False, "Szerverhiba történt a lemondási folyamat során."
