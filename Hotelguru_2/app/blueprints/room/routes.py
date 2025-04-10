from app.blueprints.room import bp
from app.blueprints.room.schemas import (
    RoomSchema,
    RoomRequestSchema,
    RoomResponseSchema,
    AllRoomListSchema,
    RoomUpdateSchema,
    RoomAdminListSchema,
    RoomAvailabilityQuerySchema,
)
from app.blueprints.room.service import RoomService
from apiflask.fields import String, Integer
from apiflask import HTTPError
from flask_jwt_extended import jwt_required  # JWT védelemhez
from app.utils.decorators import roles_required  # Szerepkör ellenőrzéshez
from app import auth  # auth importálása a JWT-hez
from app.models.association_tables import reservation_room 


@bp.route("/")
def index():
    return "This is The Room Blueprint"


@bp.get("/list/")  # Ez az elérhető szobákra
@bp.output(AllRoomListSchema(many=True))
def room_list_all():
    success, response = RoomService.room_list_all()
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=500 if not success else 400)


@bp.get("/show/by-number/<int:room_number>")  # Ez a szoba szám alapján keres
@bp.output(RoomSchema)
# @jwt_required() # Kell ide védelem? Vendég is megnézhet egy szobát? Döntsük el.
def get_room_by_number_route(room_number):
    """Visszaadja egy adott számú elérhető szoba részleteit."""
    success, response = RoomService.get_room_by_number(room_number)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=404)


##@bp.put('/update/<int:rid>') # Itt rid = ID
##@bp.doc(tags=["room", "admin"]) # Jelöljük, hogy ez inkább admin funkció lehet
##@jwt_required() # Mindenképp védjük! TODO: Szerepkör ellenőrzés (admin/recepciós?)
##@bp.input(RoomUpdateSchema, location="json")
##@bp.output(RoomResponseSchema)
##def room_update(rid, json_data):
##    success, response = RoomService.room_add(json_data)
##    if success:
##        return response, 201
##    raise HTTPError(message=response, status_code=400)

# Redundáns volt, ezért kommentelve lett, már csak az admin blueprint része
# @bp.put('/update/<int:rid>') # Ez ID alapján módosít
# @jwt_required() # JWT védelemhez
# @roles_required('Administrator') # Csak admin jogosultságú felhasználók férhetnek hozzá
# @bp.input(RoomUpdateSchema, location="json")
# @bp.output(RoomResponseSchema)
# def room_update(rid, json_data):
#    success, response = RoomService.room_update(rid, json_data)
#    if success:
#        return response, 200
#    # Ha az ID nem található, 404
#    raise HTTPError(message=response, status_code=404 if response=="Room not found!" else 400)


@bp.get("/list_all_admin")
@jwt_required()  # JWT védelemhez
#@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@roles_required("Administrator")  # Csak admin jogosultságú felhasználók férhetnek hozzá
@bp.output(RoomAdminListSchema(many=True))  # Az új admin sémát használja
# TODO: Ide majd adj hozzá jogosultság ellenőrzést! Pl.: @require_admin_role
def list_all_rooms_admin_route():
    """
    Listázza az összes szobát (admin nézet).

    Visszaadja az összes rendszerben lévő szobát, beleértve az
    elérhetőségi státuszukat is. Jogosultsaágot majd állítani kell
    """
    success, response = RoomService.list_all_rooms_admin()
    if success:
        return response, 200
    # Belső hiba esetén 500
    raise HTTPError(message=response, status_code=500)

@bp.get("/rooms/available") # Új útvonal, pl. /api/room/rooms/available
@bp.input(RoomAvailabilityQuerySchema, location='query') # Query paraméterek beolvasása
@bp.output(AllRoomListSchema(many=True)) # Kimeneti séma ugyanaz
@bp.doc(summary="Find Available Rooms by Date",
        description="Lists rooms that are generally available and not booked within the specified date range. Returns all generally available rooms if no dates are provided.")
def find_rooms(query_data):
    """
    Visszaadja azokat a szobákat, amelyek elérhetők a megadott dátumtartományban.
    Query paraméterek: ?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    """
    start_date = query_data.get('start_date')
    end_date = query_data.get('end_date')

    # Csak akkor adjuk át a dátumokat, ha mindkettő meg van adva
    if start_date and end_date:
        success, response_or_error = RoomService.find_available_rooms(start_date, end_date)
    else:
         # Ha csak az egyik vagy egyik sem, akkor lekérjük az összes általánosan elérhetőt
        success, response_or_error = RoomService.find_available_rooms() # Dátumok nélkül

    if success:
        return response_or_error
    else:
        # A service hibaüzenetet ad vissza False esetén
        # Lehetne specifikusabb hibakódot adni dátumhiba esetén (pl. 400)
        if "dátumnak korábban kell lennie" in response_or_error:
             raise HTTPError(400, message=response_or_error)
        else:
             raise HTTPError(500, message=response_or_error)

