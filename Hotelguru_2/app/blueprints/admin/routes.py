from apiflask import APIBlueprint, HTTPError

from app.blueprints.admin import bp
from app.blueprints.admin.schemas import RoomAdminSchema, ServiceAdminSchema
from app.blueprints.admin.service import AdminService
from flask import jsonify, request
from flask_jwt_extended import jwt_required  # JWT védelemhez
from app import auth  # auth importálása a JWT-hez
from app.utils.decorators import roles_required  # Szerepkör ellenőrzéshez
from app.blueprints.room.schemas import RoomRequestSchema, RoomResponseSchema # Vagy RoomAdminSchema?


print("DEBUG: Running admin blueprint routes.py")


# bp = APIBlueprint('admin', __name__, tag="Admin")
@bp.get("/test")  # Egy új, egyszerű teszt útvonal
def admin_test_route():
    print("DEBUG: admin_test_route CALLED!")  # Figyeljük, meghívódik-e
    return {"message": "Admin test route OK"}


# <<< Itt ne legyen semmi más route definíció egyelőre >>>

print("DEBUG: Running admin blueprint routes.py - AFTER route definition")


@bp.route("/")
def index():
    return "Admin Felület"


@bp.get("/")
def admin_index():
    return {"message": "Admin blueprint root OK"}


@bp.get("/rooms")
@jwt_required()
@bp.auth_required(auth)  #  Jelzi a Swaggernek, hogy auth kell
@roles_required("Administrator")  # Csak admin jogosultságú felhasználók férhetnek hozzá
@bp.output(RoomAdminSchema(many=True))
def list_all_rooms():
    success, response = AdminService.get_all_rooms()
    if success:
        return response, 200
    raise HTTPError(400, message=response)


@bp.put("/rooms/<int:room_id>")
@jwt_required()
#@bp.auth_required(auth)  #  Jelzi a Swaggernek, hogy auth kell
@roles_required("Administrator")
@bp.input(RoomAdminSchema(partial=True), arg_name="room_data")
@bp.output(RoomAdminSchema)
@bp.doc(
    summary="Update Room Details", description="Updates details of a specific room."
)
def update_room(room_id, room_data):
    """Frissíti a szoba adatait."""
    success, response_or_room = AdminService.update_room(room_id, room_data)

    if success:
        return response_or_room
    else:
        message = response_or_room
        if "nem található" in message.lower():
            raise HTTPError(404, message=message)
        else:
            raise HTTPError(400, message=message)


@bp.delete("/rooms/<int:room_id>")
@jwt_required()
#@bp.auth_required(auth)  #  Jelzi a Swaggernek, hogy auth kell
@roles_required("Administrator")  # Csak admin jogosultságú felhasználók férhetnek hozzá
def delete_room(room_id):
    success, response = AdminService.delete_room(room_id)
    if success:
        return jsonify(message=response), 200
    raise HTTPError(400, message=response)

@bp.post("/rooms")
@jwt_required()
# @bp.auth_required(auth) # Ezt valószínűleg már kivetted
@roles_required("Administrator")
@bp.input(RoomRequestSchema) # Input séma
@bp.output(RoomAdminSchema, status_code=201)
@bp.doc(summary="Add a New Room", description="Creates a new room in the system.")
def add_new_room(json_data): # <<< ÁTNEVEZVE json_data-ra
    """Új szoba hozzáadása a rendszerhez."""
    # A service hívásban is json_data-t használunk
    success, result_or_error = AdminService.add_room(json_data) # <<< ÁTNEVEZVE json_data-ra

    if success:
        return result_or_error
    else:
        if "már létezik" in result_or_error:
            raise HTTPError(409, message=result_or_error)
        elif "Érvénytelen" in result_or_error or "Hiányzó" in result_or_error:
            raise HTTPError(400, message=result_or_error)
        else:
            raise HTTPError(500, message=result_or_error)