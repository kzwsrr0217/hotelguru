from app.blueprints.receptionist import bp
from app.blueprints.receptionist.schemas import (
    ReservationReceptionistSchema,
    ReservationUpdateStatusSchema,
)
from .schemas import AddServicesSchema, InvoiceSummarySchema
from app.blueprints.receptionist.service import ReceptionistService
from apiflask import HTTPError
from flask_jwt_extended import jwt_required  # JWT védelemhez
from app import auth  # auth importálása a JWT-hez
from app.utils.decorators import roles_required  # Szerepkör ellenőrzéshez

from flask import jsonify  # Vagy használjuk ezt egyszerű üzenethez
from app.blueprints.reservation.schemas import SuccessMessageSchema
from apiflask.fields import String


@bp.get("/reservations")
@jwt_required()
@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@roles_required(
    "Receptionist", "Administrator"
)  # Csak recepciós és admin jogosultságú felhasználók férhetnek hozzá
@bp.output(ReservationReceptionistSchema(many=True))
def list_reservations():
    """Összes foglalás listázása"""
    success, response = ReceptionistService.get_all_reservations()
    if success:
        return response, 200
    raise HTTPError(400, message=response)


@bp.patch("/reservations/<int:reservation_id>/status")
@jwt_required()
@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@roles_required(
    "Receptionist", "Administrator"
)  # Csak recepciós és admin jogosultságú felhasználók férhetnek hozzá
@bp.input(ReservationUpdateStatusSchema, location="json")
def update_reservation_status(reservation_id, json_data):
    """Foglalás státuszának módosítása"""
    success, response = ReceptionistService.update_status(
        reservation_id, json_data["status"]
    )
    if success:
        return {"message": response}, 200
    raise HTTPError(400, message=response)


# --- Új Check-in Route ---
@bp.post("/checkin/<int:reservation_id>")
@jwt_required()
@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@roles_required(
    "Receptionist", "Administrator"
)  # Csak recepciós és admin jogosultságú felhasználók férhetnek hozzá
@bp.doc(
    summary="Guest Check-in",
    description="Checks in a guest for a specific reservation.",
)
@bp.output(
    SuccessMessageSchema, status_code=200, description="Guest checked in successfully."
)
def guest_check_in(reservation_id):
    """Végpont a vendég bejelentkeztetéséhez"""
    # TODO: Szerepkör ellenőrzés implementálása

    success, message = ReceptionistService.check_in_guest(reservation_id)

    if success:

        return {"message": message}
    else:
        # ... (hibakezelés marad ugyanaz a raise HTTPError-ral)
        if "nem található" in message.lower() or "not found" in message.lower():
            raise HTTPError(404, message=message)
        else:
            raise HTTPError(400, message=message)


@bp.post("/checkout/<int:reservation_id>")
@jwt_required()
@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@roles_required(
    "Receptionist", "Administrator"
)  # Csak recepciós és admin jogosultságú felhasználók férhetnek hozzá
@bp.doc(
    summary="Guest Check-out",
    description="Checks out a guest for a specific reservation and finalizes the invoice.",
)
@bp.output(SuccessMessageSchema, status_code=200)
def guest_check_out(reservation_id):
    """Végpont a vendég kijelentkeztetéséhez"""
    # TODO: Szerepkör ellenőrzés implementálása

    success, message = ReceptionistService.checkout_guest(reservation_id)

    if success:
        return {"message": message}
    else:

        if "nem található" in message.lower() or "not found" in message.lower():
            raise HTTPError(404, message=message)
        elif "Számla generálási hiba" in message:
            raise HTTPError(500, message=message)
        else:
            raise HTTPError(400, message=message)


@bp.post("/reservations/<int:reservation_id>/services")
@jwt_required()
@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@roles_required("Receptionist", "Administrator")  # Csak R/A adhat hozzá
@bp.input(AddServicesSchema, location="json")  # Input séma definiálása
@bp.output(InvoiceSummarySchema, status_code=200)  # Kimeneti séma (frissített számla)
@bp.doc(
    summary="Add Services to Reservation",
    description="Adds specified services to an active (CheckedIn) reservation's invoice.",
)
def add_services(reservation_id, json_data):
    """Végpont szolgáltatások hozzáadásához egy foglaláshoz."""
    # TODO: Szerepkör ellenőrzés

    service_ids = json_data.get(
        "service_ids", []
    )  # Kinyerjük az ID-kat a JSON body-ból

    if not service_ids:
        raise HTTPError(400, message="A 'service_ids' lista nem lehet üres.")

    success, result_or_message = ReceptionistService.add_services_to_reservation(
        reservation_id, service_ids
    )

    if success:
        # Ha sikeres, a 'result_or_message' az Invoice objektum
        # Az InvoiceSummarySchema automatikusan kiválogatja a szükséges mezőket
        return result_or_message
    else:
        # Ha nem sikeres, a 'result_or_message' a hibaüzenet string
        if (
            "nem található" in result_or_message.lower()
            or "not found" in result_or_message.lower()
        ):
            raise HTTPError(404, message=result_or_message)
        elif "Szerverhiba" in result_or_message:
            raise HTTPError(
                500, message="Hiba történt a szolgáltatások hozzáadása során."
            )
        else:
            # Minden más üzleti logikai hiba (rossz státusz, érvénytelen ID, stb.)
            raise HTTPError(400, message=result_or_message)
