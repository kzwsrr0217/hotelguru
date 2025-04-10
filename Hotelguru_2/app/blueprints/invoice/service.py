from app.extensions import db

# Szükséges modellek importálása
from app.models.reservation import Reservation, StatusEnum as ReservationStatusEnum
from app.models.invoice import Invoice, StatusEnum as InvoiceStatusEnum
from app.models.room import Room
from app.models.service import Service
from datetime import (
    datetime,
)  # Dátumokhoz kellhet, bár itt inkább a reservation datumból számolunk
import os
import tempfile
import logging  # Logoláshoz
from app.models.user import User
from typing import Union


# Weasyprint import
try:
    from weasyprint import HTML

    WEASYPRINT_INSTALLED = True
except ImportError:
    logging.warning("WeasyPrint not installed. PDF generation will be unavailable.")
    WEASYPRINT_INSTALLED = False


class InvoiceService:

    @staticmethod
    def _calculate_invoice_amount(reservation: Reservation) -> float:
        """
        Kiszámítja egy foglalás teljes számlaösszegét.
        (Segédfüggvény, a külső hívásokhoz lehet majd egy másik.)

        Args:
            reservation: A Reservation objektum, amelyhez a számla tartozik.

        Returns:
            A kiszámított végösszeg (float).
            None, ha a foglalás nem található vagy hiba történik.
        """
        if not reservation:
            return 0.0  # Vagy None, vagy hibát dobhatnánk

        try:
            # Napok számának kiszámítása - napok különbsége alapján

            num_nights = (reservation.end_date - reservation.start_date).days
            if num_nights <= 0:
                num_nights = 1  # Minimum 1 éjszaka/nap díja

            # Szobaárak összegzése
            total_room_price = 0
            if reservation.rooms:
                for room in reservation.rooms:
                    total_room_price += room.price * num_nights

            # Szolgáltatások árának összegzése
            total_service_price = 0
            if reservation.invoice:
                linked_services = (
                    db.session.query(Service)
                    .join(Invoice.services)
                    .filter(Invoice.id == reservation.invoice.id)
                    .all()
                )
                for service in linked_services:
                    total_service_price += service.price

            total_amount = total_room_price + total_service_price
            return total_amount

        except Exception as e:
            logging.exception(
                f"Error calculating invoice amount for reservation {reservation.id}: {e}"
            )
            return 0.0

    @staticmethod
    def get_or_create_invoice(
        reservation_id: int, calculate_final_amount=True
    ) -> Union[Invoice, None]:
        """
        Lekérdezi a foglaláshoz tartozó számlát, vagy létrehoz egyet, ha nem létezik.
        Opcionálisan kiszámítja és frissíti a végösszeget.

        Args:
            reservation_id: A foglalás azonosítója.
            calculate_final_amount: Ha True, kiszámítja és frissíti az összeget.

        Returns:
            Az Invoice objektum vagy None hiba esetén.
        """
        try:
            reservation = db.session.get(Reservation, reservation_id)
            if not reservation:
                logging.error(
                    f"Invoice generation failed: Reservation {reservation_id} not found."
                )
                return None

            # Megnézzük, van-e már számla ehhez a foglaláshoz
            invoice = (
                db.session.query(Invoice)
                .filter_by(reservation_id=reservation.id)
                .one_or_none()
            )

            if not invoice:
                # Ha nincs, létrehozunk egy újat (kezdetben 0 összeggel)
                logging.info(f"Creating new invoice for reservation {reservation_id}.")
                invoice = Invoice(
                    reservation_id=reservation.id,
                    amount=0.0,
                    status=InvoiceStatusEnum.Live,
                    # issue_date alapértelmezetten mai nap lesz
                )
                db.session.add(invoice)
                db.session.flush()

            # Összeg kiszámítása és frissítése, ha kérték
            if calculate_final_amount:
                logging.info(
                    f"Calculating final amount for invoice {invoice.id} (Reservation {reservation_id})."
                )
                final_amount = InvoiceService._calculate_invoice_amount(reservation)
                invoice.amount = final_amount if final_amount is not None else 0.0

            return invoice

        except Exception as e:
            logging.exception(
                f"Error getting or creating invoice for reservation {reservation_id}: {e}"
            )
            return None

    @staticmethod
    def get_invoice_details_for_pdf(invoice_id: int) -> Union[Invoice, None]:
        """
        Lekérdezi a számla adatait a PDF generáláshoz szükséges kapcsolatokkal (eager loading).
        """
        try:
            # Optimalizált lekérdezés marad
            invoice = (
                db.session.query(Invoice)
                .options(
                    db.joinedload(Invoice.reservation)
                    .joinedload(Reservation.user)
                    .joinedload(User.address),
                    db.joinedload(Invoice.reservation).joinedload(Reservation.rooms),
                    db.joinedload(Invoice.services),
                )
                .get(invoice_id)
            )

            if not invoice:
                logging.error(
                    f"Invoice details query failed: Invoice {invoice_id} not found."
                )
                return None
            if not invoice.reservation or not invoice.reservation.user:
                logging.error(
                    f"Invoice details query failed: Reservation or User not found for Invoice {invoice_id}."
                )
                return None

            # Összeg frissítése továbbra is jó ötlet lehet itt,
            # hogy a legfrissebb adatot kapja a route
            calculated_amount = InvoiceService._calculate_invoice_amount(
                invoice.reservation
            )
            if calculated_amount is None:
                logging.error(
                    f"Invoice amount calculation failed for Invoice {invoice_id}."
                )
                # Dönthetünk, hogy None-t adunk vissza, vagy a meglévő összeggel megyünk tovább
                # Most adjunk vissza None-t, jelezve a hibát
                return None
            invoice.amount = calculated_amount
            # Mivel ez csak lekérdezés + összeg beállítás, commit nem kell itt,
            # a route csak olvasni fogja az adatokat.

            return invoice  # Visszaadjuk a teljes Invoice objektumot

        except Exception as e:
            logging.exception(
                f"Error fetching invoice details for PDF (invoice_id={invoice_id}): {e}"
            )
            return None
