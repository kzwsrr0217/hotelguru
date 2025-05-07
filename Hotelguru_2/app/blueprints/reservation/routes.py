# Hotelguru_2/app/blueprints/reservation/routes.py

from flask_jwt_extended import jwt_required, get_jwt_identity
from apiflask import HTTPError

# Helyi importok
from . import bp
from .schemas import (
    ReservationListSchema,
    ReservationRequestSchema,
    ReservationResponseSchema,
    ReservationByUserSchema,
    SuccessMessageSchema,
    # ReservationUpdateSchema, # Eltávolítva, mert nincs használva és a schemas.py-ban sincs
)
from .service import ReservationService

# Szükséges importok a szolgáltatás hozzáadásához
# Használjuk a receptionist sémát, ha az megfelel az { "service_ids": [...] } formátumnak
from app.blueprints.receptionist.schemas import AddServicesSchema
# Használjuk az invoice sémát a válaszhoz (pl. az ID és az új összeg)
# Fontos: Ha az InvoiceSchema komplexebb, lehet, hogy egy egyszerűbb kellene ide
from app.blueprints.invoice.schemas import InvoiceSchema as InvoiceSummarySchema 
from app import auth # Auth importálása Swaggerhez (ha kell)
from app.utils.decorators import roles_required # Recepciós/Admin jogosultsághoz


@bp.route("/")
def index():
    return "This is The Reservation Blueprint"


@bp.get("/list/")
@jwt_required()
@bp.auth_required(auth)
@roles_required("Receptionist", "Administrator")
@bp.output(ReservationListSchema(many=True))
def reservation_list_all():
    """Összes foglalás listázása (Recepció/Admin)."""
    success, response = ReservationService.reservation_list_all()
    if success:
        return response, 200
    raise HTTPError(500, message=response)


@bp.get("/list_by_room/by-number/<int:room_number>")
@bp.output(ReservationListSchema(many=True))
@jwt_required()
@bp.auth_required(auth)
@roles_required("Receptionist", "Administrator")
def reservation_list_by_room(room_number):
    """Listázza egy adott szoba foglalásait szám alapján (Recepció/Admin)."""
    success, response = ReservationService.serach_reservation_by_room(room_number)
    if success:
        return response, 200
    raise HTTPError(500, message=response)


@bp.get("/search_by_id/<int:rid>")
@jwt_required()
@bp.auth_required(auth)
@roles_required("Receptionist", "Administrator")
@bp.output(ReservationListSchema)
def reservation_search_by_id(rid):
    """Foglalás keresése azonosító alapján (Recepció/Admin)."""
    success, response = ReservationService.serach_reservation_by_id(rid)
    if success:
        return response, 200
    raise HTTPError(404 if "nem található" in str(response).lower() else 400, message=response)


@bp.get("/list_by_user/<int:uid>")
@jwt_required()
@bp.auth_required(auth)
@roles_required("Receptionist", "Administrator")
@bp.output(ReservationByUserSchema(many=True))
def reservation_by_user(uid):
    """Adott felhasználó aktív foglalásainak listázása (Recepció/Admin)."""
    # Itt is érdemes lenne ellenőrizni, hogy létezik-e a user, mielőtt a service-t hívnánk
    success, response = ReservationService.serach_reservation_by_user(uid)
    if success:
        return response, 200
    raise HTTPError(400, message=response)


@bp.post("/add")
@jwt_required()
# @bp.auth_required(auth) # Swaggerhez, ha kell
@bp.input(ReservationRequestSchema, location="json")
@bp.output(ReservationResponseSchema, status_code=201)
def reservation_add(json_data):
    """Új foglalás létrehozása a bejelentkezett felhasználó számára."""
    current_user_id_str = get_jwt_identity()
    try:
        current_user_id = int(current_user_id_str)
    except (ValueError, TypeError):
        raise HTTPError(401, message="Érvénytelen felhasználói azonosító a tokenben.")

    success, response_or_error = ReservationService.add_reservation(current_user_id, json_data)
    if success:
        return response_or_error # Service adja a helyes sémát
    
    # Hibakezelés: Konfliktus (409), Rossz kérés/Validáció (400), Szerverhiba (500)
    if "Konfliktus" in str(response_or_error):
        raise HTTPError(409, message=response_or_error)
    elif "Hiba:" in str(response_or_error) or "Hiányzó" in str(response_or_error):
         raise HTTPError(400, message=response_or_error)
    else:
        raise HTTPError(500, message=response_or_error)


@bp.post("/<int:reservation_id>/confirm") # Áthelyezve ide a receptionist-ból logikailag?
@jwt_required()
@bp.auth_required(auth)
@roles_required("Receptionist", "Administrator")
@bp.output(SuccessMessageSchema, status_code=200)
@bp.doc(
    tags=["reservation", "receptionist", "admin"], # Címkék frissítése
    summary="Confirm Reservation",
    description="Confirms a 'Depending' reservation, changing status to 'Success' after overlap check.",
)
def confirm_reservation_route(reservation_id):
    """Foglalás visszaigazolása (Recepció/Admin)."""
    # Hívhatnánk itt is a ReservationService-t, ha oda áttesszük a logikát
    from app.blueprints.receptionist.service import ReceptionistService # Ideiglenesen innen hívjuk
    success, message = ReceptionistService.confirm_reservation(reservation_id) # Még mindig a recepciós service-t hívja
    if success:
        return {"message": message}
    else:
        if "nem található" in message.lower():
            raise HTTPError(404, message=message)
        else:
            raise HTTPError(400, message=message) # Státusz vagy ütközési hiba


@bp.delete("/cancel/<int:reservation_id>")
@jwt_required()
# @bp.auth_required(auth) # Kikommentelve, a service-ben van a jogosultság ellenőrzés
@bp.doc(
    tags=["reservation", "guest"], # Vendég is használhatja
    summary="Cancel Reservation",
    description="Allows a logged-in user to cancel their own reservation based on rules.",
)
@bp.output(SuccessMessageSchema, status_code=200)
def cancel_reservation(reservation_id):
    """Foglalás lemondása (Vendég vagy Admin/Recepciós)."""
    current_user_id_str = get_jwt_identity()
    try:
        current_user_id = int(current_user_id_str)
    except (ValueError, TypeError):
        raise HTTPError(401, message="Érvénytelen felhasználói azonosító a tokenben.")

    success, response_message = ReservationService.cancel_reservation(
        reservation_id, current_user_id
    )

    if success:
        return {"message": response_message}
    else:
        if "nem található" in response_message.lower():
            raise HTTPError(404, message=response_message)
        elif "Tiltott" in response_message or "Nincs jogosultsága" in response_message:
             raise HTTPError(403, message=response_message)
        else: # Pl. rossz státusz, határidőn túl
            raise HTTPError(400, message=response_message)


@bp.get("/reservations/mine")
@jwt_required()
# @bp.auth_required(auth) # Swaggerhez, ha kell
@bp.output(ReservationByUserSchema(many=True))
@bp.doc(tags=["reservation", "guest"], summary="Get My Reservations", description="Fetches all non-cancelled reservations for the currently logged-in user.")
def get_my_reservations():
    """Lekéri a bejelentkezett felhasználó saját foglalásait."""
    try:
        current_user_id_str = get_jwt_identity()
        current_user_id = int(current_user_id_str)
    except (ValueError, TypeError):
         raise HTTPError(401, message="Érvénytelen felhasználói azonosító a tokenben.")

    success, response_or_error = ReservationService.serach_reservation_by_user(current_user_id)
    if success:
        return response_or_error
    raise HTTPError(500, message=response_or_error)


# --- ÚJ VÉGPONT: SZOLGÁLTATÁSOK HOZZÁADÁSA SAJÁT FOGLALÁSHOZ (VENDÉG ÁLTAL) ---
@bp.post("/<int:reservation_id>/services")
@jwt_required()
# @bp.auth_required(auth) # Kikommentelhető, ha a service kezeli a jogosultságot
@bp.input(AddServicesSchema, location="json") # Input: {"service_ids": [1, 2]}
@bp.output(InvoiceSummarySchema, status_code=200) # Kimenet: frissített számla adatai
@bp.doc(
    tags=["reservation", "guest"],
    summary="Add Services to My Reservation",
    description="Allows a logged-in user to add services to their own active ('Success' or 'CheckedIn') reservation."
)
def add_services_to_my_reservation(reservation_id, json_data):
    """Végpont, ahol a vendég szolgáltatásokat adhat a saját foglalásához."""
    try:
        current_user_id_str = get_jwt_identity()
        current_user_id = int(current_user_id_str)
    except (ValueError, TypeError):
        raise HTTPError(401, message="Érvénytelen felhasználói azonosító a tokenben.")

    service_ids = json_data.get("service_ids", [])
    if not service_ids:
        raise HTTPError(400, message="A 'service_ids' lista nem lehet üres.")

    # Az új service metódus hívása
    success, result_or_message = ReservationService.add_services_to_own_reservation(
        current_user_id, reservation_id, service_ids
    )

    if success:
        # Sikeres válasz: a frissített Invoice objektum (az InvoiceSummarySchema formázza)
        return result_or_message
    else:
        # Hibaüzenet kezelése a service-től
        if "nem található" in result_or_message.lower():
            raise HTTPError(404, message=result_or_message)
        elif "Nincs jogosultsága" in result_or_message or "nem megfelelő" in result_or_message or "már le van zárva" in result_or_message:
            raise HTTPError(403, message=result_or_message)
        elif "Érvénytelen vagy inaktív" in result_or_message:
            raise HTTPError(400, message=result_or_message)
        else: # Általános szerverhiba
            raise HTTPError(500, message=result_or_message)

# --- /ÚJ VÉGPONT VÉGE ---

# Régi JWT teszt végpont (opcionális, maradhat vagy törölhető)
@bp.get("/jwt_test")
@jwt_required()
def jwt_test_endpoint():
    """JWT token érvényességének tesztelése."""
    current_user_id = get_jwt_identity()
    return {"message": "JWT Test OK!", "user_id": current_user_id}, 200