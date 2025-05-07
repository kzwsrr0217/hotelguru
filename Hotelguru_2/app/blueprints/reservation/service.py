# Hotelguru_2/app/blueprints/reservation/service.py

from app.extensions import db
from typing import Union
from app.blueprints.reservation.schemas import (
    ReservationResponseSchema,
    ReservationListSchema,
    ReservationByUserSchema,
)
from app.models.user import User
from app.models.room import Room
from app.models.reservation import Reservation, StatusEnum # Csak egyszer importáljuk
from app.models.service import Service
from app.models.invoice import Invoice, StatusEnum as InvoiceStatusEnum
from app.blueprints.invoice.service import InvoiceService
from sqlalchemy import select, and_, or_, exists, not_
from sqlalchemy.orm import selectinload
import logging
from datetime import date, datetime, timedelta
from app.models.association_tables import reservation_room

MIN_CANCELLATION_DAYS = 2


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
            if exclude_reservation_id is not None:
                query = query.filter(Reservation.id != exclude_reservation_id)

            overlapping_reservation = (
                db.session.execute(query.limit(1)).scalars().first()
            )

            if overlapping_reservation:
                logging.warning(
                    f"Overlap detected for Room ID {room_id} on dates {start_date}-{end_date}. "
                    f"Conflicting Res ID: {overlapping_reservation.id}"
                    f"{f' (Excluding Res ID: {exclude_reservation_id})' if exclude_reservation_id else ''}"
                )
                return True
            else:
                return False
        except Exception as e:
            logging.exception(f"Error during overlap check for Room ID {room_id}: {e}")
            return True # Hiba esetén biztonságosabb az átfedést jelezni

    @staticmethod
    def add_services_to_own_reservation(user_id: int, reservation_id: int, service_ids: list[int]):
        """
        Szolgáltatás(oka)t ad hozzá egy bejelentkezett felhasználó saját, aktív foglalásához
        és frissíti a hozzá tartozó számlát.
        """
        try:
            reservation = db.session.get(Reservation, reservation_id)
            if not reservation:
                return False, "Foglalás nem található."

            if reservation.user_id != user_id:
                logging.warning(f"User {user_id} attempt to add services to reservation {reservation_id} not owned by them.")
                return False, "Nincs jogosultsága ehhez a foglaláshoz szolgáltatást adni."

            if reservation.status not in [StatusEnum.Success, StatusEnum.CheckedIn]:
                return (
                    False,
                    f"Szolgáltatás nem adható hozzá: A foglalás státusza nem megfelelő ('{reservation.status.name}'). Csak 'Success' vagy 'CheckedIn' státusz esetén lehetséges."
                )

            invoice = InvoiceService.get_or_create_invoice(reservation_id, calculate_final_amount=False)
            if not invoice:
                return False, "Hiba történt a számla lekérése/létrehozása közben."

            if invoice.status == InvoiceStatusEnum.Closed:
                return False, "Szolgáltatás nem adható hozzá: A számla már le van zárva."

            services_to_add_query = db.select(Service).filter(
                Service.id.in_(service_ids),
                Service.deleted == 0
            )
            services_to_add = db.session.execute(services_to_add_query).scalars().all()

            found_ids = {s.id for s in services_to_add}
            missing_ids = [sid for sid in service_ids if sid not in found_ids]
            if missing_ids:
                logging.warning(
                    f"Add services by guest: Invalid or inactive service IDs: {missing_ids} for Res ID: {reservation_id}"
                )
                return False, f"Érvénytelen vagy inaktív szolgáltatás ID(k): {', '.join(map(str, missing_ids))}."

            if not services_to_add:
                return False, "Nincsenek érvényes szolgáltatások a hozzáadáshoz."

            added_count = 0
            for service_obj in services_to_add:
                if service_obj not in invoice.services:
                    invoice.services.append(service_obj)
                    added_count += 1
                    logging.info(
                        f"Service {service_obj.id} ({service_obj.name}) staged to be added to invoice {invoice.id} by user {user_id}."
                    )
                else:
                    logging.info(f"Service {service_obj.id} already on invoice {invoice.id}. Skipping.")

            if added_count > 0:
                # Csak akkor számoljuk újra az összeget, ha ténylegesen adtunk hozzá szolgáltatást
                updated_amount = InvoiceService._calculate_invoice_amount(reservation)
                if updated_amount is not None:
                    invoice.amount = updated_amount
                else:
                    # Ha a számítás sikertelen, vonjuk vissza a tranzakciót
                    db.session.rollback()
                    logging.error(f"Failed to recalculate invoice amount for invoice {invoice.id} after adding services.")
                    return False, "Hiba történt a számla végösszegének frissítésekor."

                # used_services string frissítése a ténylegesen hozzáadott szolgáltatások alapján
                current_used_service_ids = {s.id for s in invoice.services}
                invoice.used_services = ','.join(map(str, sorted(list(current_used_service_ids))))

                db.session.commit()
                logging.info(
                    f"{added_count} service(s) successfully added to invoice {invoice.id} for reservation {reservation_id} by user {user_id}. New amount: {invoice.amount}"
                )
                return True, invoice
            else:
                # Ha nem adtunk hozzá új szolgáltatást (mert már mind rajta volt)
                return False, "A kért szolgáltatások már szerepelnek a számlán, vagy nem volt érvényes szolgáltatás megadva."

        except Exception as ex:
            db.session.rollback()
            logging.exception(
                f"Error adding services to own reservation (Res ID: {reservation_id}, User ID: {user_id}): {ex}"
            )
            return False, "Szerverhiba történt a szolgáltatások hozzáadása során."

    @staticmethod
    def add_reservation(user_id_from_token: int, request_data: dict):
        """Új foglalás hozzáadása."""
        try:
            required_keys = ["start_date", "end_date", "room_numbers"]
            if not all(key in request_data for key in required_keys):
                missing_keys = [key for key in required_keys if key not in request_data]
                return False, f"Hiányzó adatok a kérésben: {', '.join(missing_keys)}"

            if not request_data.get("room_numbers"):
                return False, "Legalább egy szobaszámot meg kell adni."

            user = db.session.get(User, user_id_from_token)
            if not user:
                logging.warning(f"User not found with ID from token: {user_id_from_token}")
                return False, "Hiba: A megadott felhasználó nem található."

            try:
                # Dátumok validálása és átalakítása, ha szükséges
                # Feltételezzük, hogy a ReservationRequestSchema már date objektumokat ad
                start_date = request_data["start_date"]
                end_date = request_data["end_date"]
                reservation_date = request_data.get("reservation_date", date.today())

                if not isinstance(start_date, date) or not isinstance(end_date, date) or not isinstance(reservation_date, date):
                     # Ha stringként érkezik (pl. JSON-ból), akkor konvertáljuk
                    try:
                        if isinstance(start_date, str):
                            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                        if isinstance(end_date, str):
                            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                        if isinstance(reservation_date, str):
                             reservation_date = datetime.strptime(reservation_date, '%Y-%m-%d').date()
                        # Ha a típus még mindig nem megfelelő, hibát dobunk
                        if not isinstance(start_date, date) or not isinstance(end_date, date) or not isinstance(reservation_date, date):
                            raise TypeError("Érvénytelen dátum típus a konverzió után.")
                    except (ValueError, TypeError) as date_err:
                        return False, f"Érvénytelen dátumformátum vagy típus: {date_err}"


                if start_date >= end_date:
                    return False, "Hiba: A kezdő dátumnak korábban kell lennie, mint a befejező dátum."
                if start_date < date.today():
                    return False, "Hiba: Foglalás csak a mai naptól kezdődően lehetséges."

            except KeyError as ke:
                return False, f"Hiányzó kötelező mező a kérésben: {ke}"
            except Exception as e: # Általánosabb hibakezelés
                return False, f"Hiba a dátumok feldolgozásakor: {e}"


            requested_room_numbers = request_data["room_numbers"]
            selected_rooms_query = select(Room).filter(Room.number.in_(requested_room_numbers))
            selected_rooms = db.session.execute(selected_rooms_query).scalars().all()

            found_room_numbers = {room.number for room in selected_rooms}
            # Fontos: A request_data["room_numbers"] elemei lehetnek int vagy string típusúak, egységesítsük int-re
            missing_room_numbers = set(map(int, requested_room_numbers)) - set(map(int, found_room_numbers))

            if missing_room_numbers:
                return False, f"Hiba: A következő szobaszám(ok) nem léteznek: {', '.join(map(str, missing_room_numbers))}"

            if not selected_rooms:
                 return False, "Hiba: Egyetlen érvényes szoba sem található a kérésben."


            for room in selected_rooms:
                if ReservationService._check_for_overlaps(room.id, start_date, end_date):
                    return False, f"Konfliktus: A(z) {room.number} szoba már foglalt a kért időszak ({start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}) egy részére vagy egészére."

            reservation = Reservation(
                start_date=start_date,
                end_date=end_date,
                reservation_date=reservation_date,
                user_id=user.id,
                status=StatusEnum.Depending,
            )
            reservation.rooms.extend(selected_rooms)

            db.session.add(reservation)
            # Itt még nem kell commit, ha később számlát is generálunk
            # db.session.flush() # Az ID generálásához elég lehet

            # Opcionális: Számla létrehozása foglaláskor (kezdetben 0 összeggel)
            # invoice = Invoice(reservation_id=reservation.id, amount=0.0, status=InvoiceStatusEnum.Live)
            # db.session.add(invoice)

            db.session.commit() # Most már commitoljuk

            logging.info(f"Foglalás sikeresen létrehozva (ID: {reservation.id}) a felhasználónak: {user.id}")
            return True, ReservationResponseSchema().dump(reservation)

        except Exception as ex:
            db.session.rollback()
            logging.exception(f"Váratlan hiba történt a foglalás létrehozása közben (User ID: {user_id_from_token}): {ex}")
            return False, "Szerverhiba történt a foglalás feldolgozása közben."


    @staticmethod
    def reservation_list_all():
        """Listázza az összes foglalást (Admin/Recepciós számára)."""
        try:
            reservations_query = select(Reservation).options(
                selectinload(Reservation.user),
                selectinload(Reservation.rooms),
                selectinload(Reservation.invoice).selectinload(Invoice.services)
            ).order_by(Reservation.start_date.desc())
            reservations = db.session.execute(reservations_query).scalars().all()
            # Itt a nyers objektumokat adjuk vissza, a dump a route-ban történik
            return True, reservations
        except Exception as e:
            logging.exception(f"Error listing all reservations: {e}")
            return False, "Hiba a foglalások listázása közben."

    @staticmethod
    def serach_reservation_by_room(room_number: int):
        """Adott szobaszámhoz tartozó foglalások listázása (Admin/Recepciós számára)."""
        try:
            reservations_query = select(Reservation).filter(
                Reservation.rooms.any(Room.number == room_number)
            ).options(
                selectinload(Reservation.user),
                selectinload(Reservation.rooms),
                selectinload(Reservation.invoice).selectinload(Invoice.services)
            )
            reservations = db.session.execute(reservations_query).scalars().all()
            # Nyers objektumok visszaadása
            return True, reservations
        except Exception as e:
            logging.exception(f"Error searching reservations by room number {room_number}: {e}")
            return False, "Hiba a szobaszám alapján történő keresés közben."

    @staticmethod
    def serach_reservation_by_id(rid: int):
        """Foglalás keresése azonosító alapján (Admin/Recepciós számára)."""
        try:
            reservation = db.session.query(Reservation).options(
                selectinload(Reservation.user),
                selectinload(Reservation.rooms),
                selectinload(Reservation.invoice).selectinload(Invoice.services)
            ).get(rid)
            if reservation is None:
                return False, "A megadott azonosítóval nem található foglalás."
            # Nyers objektum visszaadása
            return True, reservation
        except Exception as e:
            logging.exception(f"Error searching reservation by ID {rid}: {e}")
            return False, "Hiba az azonosító alapján történő keresés közben."


    # JAVÍTOTT FÜGGVÉNY
    @staticmethod
    def serach_reservation_by_user(uid: int):
        """Adott felhasználó foglalásainak listázása - JAVÍTOTT VÁLTOZAT."""
        try:
            # A logolás maradhat, de most már nem hívunk dump-ot itt
            logging.info(f"--------------------------------------------------------------------------")
            logging.info(f"[SERVICE_SEARCH_BY_USER] START - Fetching for user ID (uid parameter): {uid} (type: {type(uid)})")

            if not isinstance(uid, int):
                logging.error(f"[SERVICE_SEARCH_BY_USER] CRITICAL: uid parameter is NOT an integer! Value: {uid}")
                return False, "Belső hiba: Érvénytelen felhasználói azonosító típus."

            visible_statuses = [
                StatusEnum.Depending,
                StatusEnum.Success,
                StatusEnum.CheckedIn,
            ]
            logging.info(f"[SERVICE_SEARCH_BY_USER] Intended filter statuses: {[s.name for s in visible_statuses]}")

            reservations_query = (
                db.select(Reservation)
                .options(
                    selectinload(Reservation.rooms).load_only(Room.number),
                    # Fontos: Eager load a számlát ÉS annak szolgáltatásait is!
                    selectinload(Reservation.invoice).selectinload(Invoice.services)
                )
                .filter(Reservation.user_id == uid)
                .filter(Reservation.status.in_(visible_statuses))
                .order_by(Reservation.start_date.desc())
            )

            logging.info(f"[SERVICE_SEARCH_BY_USER] Executing SQLAlchemy query for user {uid}...")
            reservations_list = db.session.execute(reservations_query).unique().scalars().all()
            logging.info(f"[SERVICE_SEARCH_BY_USER] Query executed. Found {len(reservations_list)} reservations for user {uid} after filters.")

            # Logolhatjuk a nyers adatokat, ha szükséges (opcionális debug)
            if reservations_list and logging.getLogger().isEnabledFor(logging.DEBUG): # Csak DEBUG szinten
                 logging.debug(f"[SERVICE_SEARCH_BY_USER] --- Raw results (first few) ---")
                 for i, res_obj in enumerate(reservations_list[:3]): # Csak az első párat
                    log_prefix = f"  RawRes #{i+1} (ID: {res_obj.id}):"
                    start_date_type = type(getattr(res_obj, 'start_date', None))
                    end_date_type = type(getattr(res_obj, 'end_date', None))
                    res_date_type = type(getattr(res_obj, 'reservation_date', None))
                    logging.debug(f"{log_prefix} Dates: {start_date_type}, {end_date_type}, {res_date_type}")
                    invoice_obj = getattr(res_obj, 'invoice', None)
                    services_info = "NoInvoice"
                    if invoice_obj and hasattr(invoice_obj, 'services'):
                         services_info = f"InvID={invoice_obj.id}, Svcs={[s.id for s in invoice_obj.services]}"
                    elif invoice_obj:
                         services_info = f"InvID={invoice_obj.id}, SvcsAttrMissingOrNone"
                    logging.debug(f"{log_prefix} Invoice/Services: {services_info}")
                 logging.debug(f"[SERVICE_SEARCH_BY_USER] --- End raw results log ---")


            logging.info(f"--------------------------------------------------------------------------")
            # A NYERS listát adjuk vissza, a séma szerializálást a @bp.output végzi
            return True, reservations_list

        except Exception as e:
            logging.exception(f"[SERVICE_SEARCH_BY_USER] CRITICAL ERROR searching reservations for user ID {uid}: {e}")
            logging.info(f"--------------------------------------------------------------------------")
            return False, "Kritikus hiba a felhasználó foglalásainak keresése közben."


    @staticmethod
    def confirm_reservation(reservation_id: int):
        """Visszaigazol egy 'Depending' státuszú foglalást 'Success'-re."""
        try:
            reservation = db.session.get(Reservation, reservation_id)
            if not reservation: return False, "Foglalás nem található."
            if reservation.status != StatusEnum.Depending: return False, f"Visszaigazolás sikertelen: Státusz '{reservation.status.name}'"
            if not reservation.rooms: return False, "Visszaigazolás sikertelen: Nincsenek szobák hozzárendelve."

            has_overlap = False
            conflicting_room_numbers = []
            for room in reservation.rooms:
                if ReservationService._check_for_overlaps(room.id, reservation.start_date, reservation.end_date, exclude_reservation_id=reservation_id):
                    has_overlap = True
                    conflicting_room_numbers.append(str(room.number))
                    # Ha találtunk egy ütközést, felesleges tovább keresni
                    break

            if has_overlap:
                return False, f"Visszaigazolás sikertelen: Ütközés a(z) {', '.join(conflicting_room_numbers)} szobá(k)nál."

            # Ha nincs ütközés, státuszváltás és mentés
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
        """Foglalás módosítása (Admin/Recepciós számára)."""
        try:
            reservation = db.session.get(Reservation, rid)
            if not reservation: return False, "Foglalás nem található!"

            # Aktuális értékek mentése, hogy csak a változásokat írjuk felül
            new_start_date = reservation.start_date
            new_end_date = reservation.end_date
            new_reservation_date = reservation.reservation_date
            new_status = reservation.status
            selected_rooms = list(reservation.rooms) # Jelenlegi szobák másolása

            # Dátumok frissítése, ha megadták
            try:
                if "start_date" in request_data:
                    start_date_input = request_data["start_date"]
                    # Dátum konverzió, ha string
                    if isinstance(start_date_input, str): new_start_date = datetime.strptime(start_date_input, "%Y-%m-%d").date()
                    elif isinstance(start_date_input, date): new_start_date = start_date_input
                    else: raise TypeError("Érvénytelen start_date típus.")
                if "end_date" in request_data:
                     end_date_input = request_data["end_date"]
                     if isinstance(end_date_input, str): new_end_date = datetime.strptime(end_date_input, "%Y-%m-%d").date()
                     elif isinstance(end_date_input, date): new_end_date = end_date_input
                     else: raise TypeError("Érvénytelen end_date típus.")
                if "reservation_date" in request_data:
                    res_date_input = request_data["reservation_date"]
                    if res_date_input is None: new_reservation_date = date.today() # Vagy maradjon az eredeti? Döntsük el.
                    elif isinstance(res_date_input, str): new_reservation_date = datetime.strptime(res_date_input, "%Y-%m-%d").date()
                    elif isinstance(res_date_input, date): new_reservation_date = res_date_input
                    else: raise TypeError("Érvénytelen reservation_date típus.")

                # Dátum logika ellenőrzése
                if new_start_date >= new_end_date: return False, "Hiba: Kezdő dátum >= Befejező dátum."
                # Lehetne itt is ellenőrizni, hogy start_date ne legyen múltbeli?
                # if new_start_date < date.today(): return False, "Hiba: A módosított kezdő dátum nem lehet múltbeli."

            except (ValueError, TypeError) as e: return False, f"Érvénytelen dátum: {e}"

            # Státusz frissítése, ha megadták
            if "status" in request_data:
                 try:
                     status_input = request_data["status"]
                     if isinstance(status_input, str): new_status = StatusEnum[status_input] # Enum név alapján
                     elif isinstance(status_input, StatusEnum): new_status = status_input
                     else: raise TypeError("Érvénytelen status típus.")
                 except (KeyError, TypeError) as e: return False, f"Érvénytelen státusz: {e}"

            # Szobák frissítése, ha megadták
            if "room_numbers" in request_data:
                 requested_room_numbers = request_data["room_numbers"]
                 if not requested_room_numbers: return False, "Legalább egy szobaszámot meg kell adni a módosításhoz."
                 # Validáljuk az új szobákat
                 rooms_query = select(Room).filter(Room.number.in_(requested_room_numbers))
                 new_selected_rooms = db.session.execute(rooms_query).scalars().all()
                 # Ellenőrizzük, hogy minden kért szoba létezik-e
                 if len(new_selected_rooms) != len(set(requested_room_numbers)): # Használjunk set-et a duplikációk kiszűrésére
                     return False, "Egy vagy több megadott szobaszám érvénytelen."
                 selected_rooms = new_selected_rooms # Felülírjuk a szobalistát az újjal

            # Ütközésvizsgálat az ÚJ dátumokkal és ÚJ szobákkal (kizárva a jelenlegi foglalást)
            new_room_ids = [room.id for room in selected_rooms]
            has_overlap = False
            conflicting_room_num = None
            for room_id_check in new_room_ids:
                 if ReservationService._check_for_overlaps(room_id_check, new_start_date, new_end_date, exclude_reservation_id=rid):
                     has_overlap = True
                     conflicting_room = db.session.get(Room, room_id_check) # Szobaszám lekérése a loghoz
                     conflicting_room_num = conflicting_room.number if conflicting_room else 'ismeretlen'
                     break # Elég egy ütközést találni
            if has_overlap: return False, f"Módosítás sikertelen: Ütközés észlelve a(z) {conflicting_room_num} szobánál a kért időszakra."

            # Ha minden rendben, alkalmazzuk a változásokat
            reservation.start_date = new_start_date
            reservation.end_date = new_end_date
            reservation.reservation_date = new_reservation_date
            reservation.status = new_status
            reservation.rooms = selected_rooms # Cseréljük le a szobákat az újakra

            # TODO: Számla összegének újraszámítása, ha a dátum vagy a szobák változtak?
            # Ezt meg kell fontolni. Ha változik az időtartam vagy a szobaár, az összeget is frissíteni kellene.
            # if new_start_date != reservation.start_date or new_end_date != reservation.end_date or \
            #    set(new_room_ids) != set(r.id for r in reservation.rooms): #<- régi szobák összehasonlítása
            #     invoice = InvoiceService.get_or_create_invoice(rid, calculate_final_amount=True)
            #     if not invoice:
            #         db.session.rollback()
            #         return False, "Hiba a számla összegének frissítésekor."

            db.session.commit()
            logging.info(f"Reservation {rid} updated successfully.")
            # Visszaadjuk a módosított foglalás nyers objektumát
            return True, reservation
        except Exception as ex:
            db.session.rollback()
            logging.exception(f"Error updating reservation {rid}: {ex}")
            return False, f"Hiba történt a(z) {rid} foglalás módosítása közben."


    @staticmethod
    def cancel_reservation(reservation_id: int, user_id: int):
        """Lemond egy foglalást."""
        try:
            reservation = db.session.get(Reservation, reservation_id)
            if not reservation: return False, "Foglalás nem található."

            user = db.session.get(User, user_id)
            if not user: return False, "Felhasználó nem található."

            # Szerepkörök ellenőrzése
            is_admin_or_receptionist = any(role.name in ["Administrator", "Receptionist"] for role in user.roles)

            # Jogosultság ellenőrzése: Vagy a sajátja, vagy admin/recepciós
            if reservation.user_id != user_id and not is_admin_or_receptionist:
                return False, "Tiltott: Csak saját foglalás mondható le, vagy megfelelő jogosultsággal."

            # Lemondási feltételek ellenőrzése
            can_cancel = False
            cancel_reason = ""
            # Lemondható státuszok: Függőben, Visszaigazolt
            if reservation.status in [StatusEnum.Depending, StatusEnum.Success]:
                # Ellenőrizzük a határidőt VAGY ha admin/recepciós próbálja
                if (reservation.start_date - date.today()).days >= MIN_CANCELLATION_DAYS or is_admin_or_receptionist:
                    can_cancel = True
                else:
                    # Vendég próbálja, de túl későn
                     cancel_reason = f"Lemondás legkésőbb {MIN_CANCELLATION_DAYS} nappal érkezés előtt lehetséges."
            else:
                cancel_reason = f"Foglalás '{reservation.status.name}' státusszal nem lemondható."

            if not can_cancel: return False, f"Lemondás sikertelen: {cancel_reason}"

            # Ha lemondható, státusz váltás és mentés
            reservation.status = StatusEnum.Canceled
            # Opcionális: A lemondott foglaláshoz tartozó szobákat újra elérhetővé tesszük?
            # Ez üzleti döntés kérdése. Most NE tegyük, mert lehet, hogy a recepció még felülbírálja.
            # for room in reservation.rooms:
            #     room.is_available = True

            # Opcionális: A hozzá tartozó számla státuszát is 'Canceled'-re állítjuk?
            if reservation.invoice:
                 reservation.invoice.status = InvoiceStatusEnum.Canceled # Invoice státuszát is átállítjuk

            db.session.commit()
            logging.info(f"Reservation {reservation_id} cancelled by user {user_id}.")
            return True, "Foglalás sikeresen lemondva."
        except Exception as ex:
            db.session.rollback()
            logging.exception(f"Error cancelling reservation {reservation_id} by user {user_id}: {ex}")
            return False, "Szerverhiba történt a lemondási folyamat során."