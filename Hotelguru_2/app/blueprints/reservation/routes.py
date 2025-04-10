from app.blueprints.reservation import bp
from app.blueprints.reservation.schemas import (
    ReservationListSchema,
    ReservationRequestSchema,
    ReservationResponseSchema,
    ReservationByUserSchema,
    SuccessMessageSchema,
)
from app.blueprints.reservation.service import ReservationService
from app.blueprints.reservation.schemas import SuccessMessageSchema

from apiflask.fields import String, Integer  # String import hozzáadása
from apiflask import HTTPError
from flask import jsonify  # jsonify import
from flask_jwt_extended import jwt_required, get_jwt_identity  # JWT védelemhez
from app import auth  # auth importálása a JWT-hez
from app.utils.decorators import roles_required  # Szerepkör ellenőrzéshez


@bp.route("/")
def index():
    return "This is The Reservation Blueprint"


@bp.get("/list/")
@jwt_required()  # JWT védelemhez
@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@roles_required(
    "Receptionist", "Administrator"
)  # Csak recepciós és admin jogosultságú felhasználók férhetnek hozzá
@bp.output(ReservationListSchema(many=True))
def reservation_list_all():
    success, response = ReservationService.reservation_list_all()
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


@bp.get("/list_by_room/by-number/<int:room_number>")  # Útvonal és paraméter átnevezve
@bp.output(ReservationListSchema(many=True))
@jwt_required()  # JWT védelemhez
@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@roles_required(
    "Receptionist", "Administrator"
)  # Csak recepciós és admin jogosultságú felhasználók férhetnek hozzá
def reservation_list_by_room(room_number):  # Paraméter átnevezve
    """Listázza egy adott szoba foglalásait (szám alapján)."""
    success, response = ReservationService.serach_reservation_by_room(
        room_number
    )  # Service hívás (paraméter nevét ott is javítani kell)
    if success:
        return response, 200
    raise HTTPError(
        message=response, status_code=404 if not response else 400
    )  # Jobb hibakezelés


@bp.get("/search_by_id/<int:rid>")
@jwt_required()  # JWT védelemhez
@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@roles_required(
    "Receptionist", "Administrator"
)  # Csak recepciós és admin jogosultságú felhasználók férhetnek hozzá
@bp.output(ReservationListSchema)
def reservation_search_by_id(rid):
    success, response = ReservationService.serach_reservation_by_id(rid)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


@bp.get("/list_by_user/<int:uid>")
@jwt_required()  # JWT védelemhez
@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@roles_required(
    "Receptionist", "Administrator"
)  # Csak recepciós és admin jogosultságú felhasználók férhetnek hozzá
@bp.output(ReservationByUserSchema(many=True))
def reservation_by_user(uid):
    success, response = ReservationService.serach_reservation_by_user(uid)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


@bp.post("/add")
@jwt_required()  # JWT védelemhez
#@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@bp.input(ReservationRequestSchema, location="json")
@bp.output(ReservationResponseSchema, status_code=201)
def reservation_add(json_data):  # json_data már nem tartalmazza a user ID-t
    current_user_id = get_jwt_identity()  # <<< Felhasználó ID kinyerése a tokenből
    # Átadjuk a user ID-t és a request body többi részét a service-nek
    success, response = ReservationService.add_reservation(current_user_id, json_data)
    if success:
        return response
    raise HTTPError(message=response, status_code=400)


"""
@bp.put('/update/<int:rid>')
@jwt_required() # JWT védelemhez
@roles_required('Receptionist', 'Administrator') # Csak recepciós és admin jogosultságú felhasználók férhetnek hozzá
@bp.input(ReservationUpdateSchema, location="json")
@bp.output(ReservationResponseSchema)
def reservation_update(rid, json_data):
    success, response = ReservationService.update_reservation(rid, json_data)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)"""


@bp.post("/reservations/<int:reservation_id>/confirm")
@jwt_required()
@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@roles_required("Receptionist", "Administrator")
@bp.output(SuccessMessageSchema, status_code=200)
@bp.doc(
    summary="Confirm Reservation",
    description="Confirms a 'Depending' reservation, changing status to 'Success' after overlap check.",
)
def confirm_reservation_route(reservation_id):
    """Végpont foglalás visszaigazolásához."""
    success, message = ReceptionistService.confirm_reservation(reservation_id)
    if success:
        return {"message": message}
    else:
        if "nem található" in message.lower():
            raise HTTPError(404, message=message)
        else:  # Minden más hiba (rossz státusz, ütközés, szerverhiba) 400-as kódot kap
            raise HTTPError(400, message=message)


@bp.delete("/cancel/<int:reservation_id>")
@jwt_required()  # JWT védelemhez
#@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
#@roles_required(
#    "Receptionist", "Administrator"
#)  # Csak recepciós és admin jogosultságú felhasználók férhetnek hozzá
@bp.doc(
    summary="Foglalás lemondása",
    description="Lehetővé teszi egy bejelentkezett felhasználó számára, hogy lemondja a saját foglalását azonosító alapján, a lemondási szabályok figyelembevételével.",
)
@bp.output(
    SuccessMessageSchema, status_code=200, description="Foglalás sikeresen lemondva."
)  # <- CSERÉLD ERRE!
def cancel_reservation(reservation_id):
    """Végpont egy foglalás lemondásához"""
    current_user_id = int(get_jwt_identity())

    success, response_message = ReservationService.cancel_reservation(
        reservation_id, current_user_id
    )

    if success:
        # <- Sima dictionary visszaadása, nem jsonify!
        return {"message": response_message}
    else:
        # ... (hibakezelés marad ugyanaz a raise HTTPError-ral)
        if (
            "nem található" in response_message.lower()
            or "not found" in response_message.lower()
        ):
            raise HTTPError(404, message=response_message)
        elif (
            "tiltott" in response_message.lower()
            or "forbidden" in response_message.lower()
            or "not authorized" in response_message.lower()
        ):
            raise HTTPError(403, message=response_message)
        else:
            raise HTTPError(400, message=response_message)

# ÚJ VÉGPONT A SAJÁT FOGLALÁSOKHOZ
@bp.get("/reservations/mine") # Új útvonal, pl. /api/reservation/reservations/mine
@jwt_required() # Csak bejelentkezés szükséges, specifikus szerepkör nem
#@bp.auth_required(auth) # Swaggerhez
@bp.output(ReservationByUserSchema(many=True)) # Ugyanaz a séma jó lesz
@bp.doc(summary="Get My Reservations", description="Fetches all non-cancelled reservations for the currently logged-in user.")
def get_my_reservations():
    """Lekéri a bejelentkezett felhasználó saját foglalásait."""
    try:
        # Felhasználó ID kinyerése a JWT tokenből
        current_user_id_str = get_jwt_identity()
        current_user_id = int(current_user_id_str) # Átalakítás int-té
    except (ValueError, TypeError):
         raise HTTPError(401, message="Érvénytelen felhasználói azonosító a tokenben.")

    # A meglévő service függvény használata az aktuális user ID-jával
    success, response = ReservationService.serach_reservation_by_user(current_user_id)
    if success:
        return response
    # A service már kezeli, ha nincs user (bár itt a token miatt lennie kell)
    # vagy ha hiba történik a lekérdezéskor
    raise HTTPError(500, message=response) # Általános szerverhiba, ha a service False-t ad vissza

@bp.get("/jwt_test")
@jwt_required() # CSAK ez a védelem van rajta!
def jwt_test_endpoint():
    """Egy egyszerű végpont annak tesztelésére, hogy a @jwt_required működik-e."""
    # Ha idáig eljut a kérés, a token valid volt.
    current_user_id = get_jwt_identity() # Próbáljuk meg ezt is kinyerni
    return jsonify(message="JWT Test OK!", user_id=current_user_id), 200