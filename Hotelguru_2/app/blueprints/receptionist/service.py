from sqlalchemy import select  # Hozzáadni
from app.extensions import db
from app.models.user import User
from app.models.reservation import Reservation, StatusEnum
from app.models.invoice import Invoice, StatusEnum as InvoiceStatusEnum
from app.models.room import Room

# Service-ek
from app.blueprints.invoice.service import InvoiceService
from app.models.service import Service

# Egyéb
from datetime import date
import logging


class ReceptionistService:
    @staticmethod
    def get_all_reservations():
        reservations = (
            db.session.execute(
                select(Reservation).order_by(Reservation.start_date.desc())
            )
            .scalars()
            .all()
        )
        return True, reservations

    @staticmethod
    def update_status(reservation_id, new_status):
        reservation = db.session.get(Reservation, reservation_id)
        if not reservation:
            return False, "Foglalás nem található"
        reservation.status = StatusEnum[new_status]
        db.session.commit()
        return True, "Státusz frissítve"

    @staticmethod
    def check_in_guest(reservation_id: int):
        """
        Vendég bejelentkeztetése egy adott foglaláshoz.

        Args:
            reservation_id: A foglalás azonosítója.

        Returns:
            Tuple[bool, str]: (sikeres_állapot, üzenet)
        """
        try:
            reservation = db.session.get(Reservation, reservation_id)

            # 1. Létezik a foglalás?
            if not reservation:
                return False, "Foglalás nem található"

            # 2. Megfelelő a státusz a check-inhez?
            # Csak 'Success' (visszaigazolt) státuszból engedünk check-int.
            # Vagy esetleg 'Depending'-ből is? Egyelőre maradjunk a Success-nél.
            if reservation.status != StatusEnum.Success:
                return (
                    False,
                    f"Check-in sikertelen: A foglalás státusza nem megfelelő ('{reservation.status.name}'). Csak visszaigazolt (Success) foglalást lehet bejelentkeztetni.",
                )

            # 3. Megfelelő a dátum a check-inhez?
            # Alapértelmezetten csak az érkezés napján engedünk check-int.
            # Lehetne +/- 1 nap tolerancia, de kezdjük ezzel.
            if reservation.start_date != date.today():
                return (
                    False,
                    f"Check-in sikertelen: A check-in csak az érkezés napján ({reservation.start_date}) lehetséges.",
                )

            # 4. Státusz frissítése 'CheckedIn'-re
            reservation.status = StatusEnum.CheckedIn
            db.session.commit()

            logging.info(f"Reservation {reservation_id} successfully checked in.")
            return True, "Vendég sikeresen bejelentkeztetve."

        except Exception as ex:
            db.session.rollback()
            logging.exception(
                f"Error during check-in for reservation {reservation_id}: {ex}"
            )
            return False, "Szerverhiba történt a check-in folyamat során."

    @staticmethod
    def checkout_guest(reservation_id: int):
        """
        Vendég kijelentkeztetése és számla véglegesítése.

        Args:
            reservation_id: A foglalás azonosítója.

        Returns:
            Tuple[bool, str]: (sikeres_állapot, üzenet/hibaüzenet)
        """
        try:
            reservation = db.session.get(Reservation, reservation_id)

            # 1. Létezik a foglalás?
            if not reservation:
                return False, "Foglalás nem található"

            # 2. Megfelelő a státusz a check-outhoz?
            # Csak 'CheckedIn' státuszból engedünk check-outot.
            if reservation.status != StatusEnum.CheckedIn:  # <<< ÚJ
                return (
                    False,
                    f"Check-out sikertelen: A foglalás státusza nem megfelelő ('{reservation.status.name}'). Csak bejelentkezett (CheckedIn) foglalást lehet kijelentkeztetni.",
                )

            # 3. Dátum ellenőrzés
            # Legalább a foglalás végének napján vagy utána lehet kijelentkezni?
            if date.today() < reservation.end_date:
                return (
                    False,
                    f"Check-out sikertelen: A kijelentkezés legkorábban a távozás napján ({reservation.end_date}) lehetséges.",
                )

            # 4. Számla lekérdezése/létrehozása és véglegesítése
            # Itt hívjuk a korábban létrehozott InvoiceService metódust
            # A calculate_final_amount=True biztosítja, hogy az összeg frissüljön
            invoice = InvoiceService.get_or_create_invoice(
                reservation_id, calculate_final_amount=True
            )

            if not invoice:
                # Ha a számlát nem sikerült lekérni/létrehozni/kiszámolni
                return False, "Számla generálási hiba a check-out során."

            # Számla státuszának beállítása 'Closed'-ra
            invoice.status = InvoiceStatusEnum.Closed
            logging.info(
                f"Invoice {invoice.id} status set to Closed for reservation {reservation_id}."
            )

            # 5. Foglalás státuszának frissítése 'CheckedOut'-ra
            reservation.status = StatusEnum.CheckedOut
            # 6. Szobák elérhetővé tétele
            if reservation.rooms:
                for room in reservation.rooms:
                    room.is_available = True
                logging.info(
                    f"Rooms made available for checked-out reservation {reservation_id}."
                )
            else:
                logging.warning(
                    f"No rooms found associated with reservation {reservation_id} during checkout."
                )

            # 7. Változtatások mentése (teljes tranzakció)
            db.session.commit()

            logging.info(f"Reservation {reservation_id} successfully checked out.")
            return True, f"Vendég sikeresen kijelentkeztetve. Számla ID: {invoice.id}"

        except Exception as ex:
            db.session.rollback()  # Visszavonjuk a teljes tranzakciót hiba esetén
            logging.exception(
                f"Error during check-out for reservation {reservation_id}: {ex}"
            )
            return False, "Szerverhiba történt a check-out folyamat során."

    @staticmethod
    def add_services_to_reservation(reservation_id: int, service_ids: list[int]):
        """
        Szolgáltatás(oka)t ad hozzá egy meglévő, bejelentkezett foglaláshoz és
        frissíti a hozzá tartozó számlát.

        Args:
            reservation_id: A cél foglalás azonosítója.
            service_ids: A hozzáadandó szolgáltatások azonosítóinak listája.

        Returns:
            Tuple[bool, Union[Invoice, str]]: (Sikeresség, Invoice objektum vagy Hibaüzenet)
        """
        try:
            reservation = db.session.get(Reservation, reservation_id)
            if not reservation:
                return False, "Foglalás nem található."

            # Csak bejelentkezett (CheckedIn) foglaláshoz adhatunk szolgáltatást
            if reservation.status != StatusEnum.CheckedIn:
                return (
                    False,
                    f"Szolgáltatás nem adható hozzá: A foglalás státusza nem megfelelő ('{reservation.status.name}'). Csak 'CheckedIn' státusz esetén lehetséges.",
                )

            # Számla lekérése vagy létrehozása (összeg újraszámolása nélkül itt)
            invoice = InvoiceService.get_or_create_invoice(
                reservation_id, calculate_final_amount=False
            )
            if not invoice:
                # Ez elvileg nem fordulhat elő, ha a foglalás létezik, de jobb ellenőrizni
                return False, "Hiba történt a számla lekérése/létrehozása közben."

            # Ellenőrizzük, hogy a számla státusza engedi-e a módosítást (pl. ne legyen 'Closed')
            if invoice.status == InvoiceStatusEnum.Closed:
                return (
                    False,
                    "Szolgáltatás nem adható hozzá: A számla már le van zárva.",
                )

            # Lekérdezzük a hozzáadni kívánt Service objektumokat
            # Csak létező és nem törölt szolgáltatásokat vegyünk figyelembe
            services_to_add = (
                db.session.query(Service)
                .filter(
                    Service.id.in_(service_ids),
                    Service.deleted == 0,  # Csak aktív szolgáltatások
                )
                .all()
            )

            # Ellenőrizzük, hogy minden kért ID-hoz találtunk-e szolgáltatást
            found_ids = {s.id for s in services_to_add}
            missing_ids = [sid for sid in service_ids if sid not in found_ids]
            if missing_ids:
                logging.warning(
                    f"Szolgáltatás hozzáadása: Nem található vagy inaktív szolgáltatás ID-k: {missing_ids} (Foglalás: {reservation_id})"
                )
                # Dönthetünk úgy, hogy csak a létezőket adjuk hozzá, vagy hibát adunk vissza
                # Most adjunk hibát vissza, ha bármelyik hiányzik:
                return (
                    False,
                    f"Szolgáltatás nem adható hozzá: A következő ID-k érvénytelenek vagy inaktívak: {missing_ids}",
                )

            if not services_to_add:
                return False, "Nincsenek érvényes szolgáltatások a hozzáadáshoz."

            added_count = 0
            # Végigmegyünk a hozzáadandó szolgáltatásokon
            for service in services_to_add:
                # Ellenőrizzük (opcionális), hogy nincs-e már hozzáadva ez a szolgáltatás?
                # Ha többször is hozzáadható (pl. napi reggeli), akkor ez a check nem kell.
                # Most feltételezzük, hogy egy típusú szolgáltatás csak egyszer szerepelhet.
                if service in invoice.services:
                    logging.warning(
                        f"Service {service.id} already on invoice {invoice.id}. Skipping."
                    )
                    continue  # Kihagyjuk, ha már rajta van

                # Hozzáadás a kapcsolótáblához (SQLAlchemy kezeli)
                invoice.services.append(service)
                # Összeg növelése
                invoice.amount += service.price
                added_count += 1
                logging.info(
                    f"Service {service.id} ({service.name}) added to invoice {invoice.id}. New amount: {invoice.amount}"
                )

            # Itt lehetne frissíteni a redundáns `used_services` stringet is, ha még használjuk
            # current_used = set(filter(None, invoice.used_services.split(',')))
            # for service in services_to_add:
            #     current_used.add(str(service.id))
            # invoice.used_services = ','.join(sorted(list(current_used)))

            db.session.commit()  # Változások mentése

            if added_count > 0:
                return True, invoice  # Visszaadjuk a frissített számla objektumot
            else:
                # Ha minden kért szolgáltatás már rajta volt a számlán
                return False, "A kért szolgáltatások már szerepelnek a számlán."

        except Exception as ex:
            db.session.rollback()
            logging.exception(
                f"Error adding services for reservation {reservation_id}: {ex}"
            )
            return False, "Szerverhiba történt a szolgáltatások hozzáadása során."
