# Hotelguru_2/app/blueprints/user/routes.py

import logging
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from apiflask import HTTPError

from app import auth, db
from app.utils.decorators import roles_required
from app.models.user import User

from . import bp # Blueprint importálása a saját mappából
from .schemas import ( # Sémák importálása a saját mappából
    UserResponseSchema,
    UserRequestSchema,
    UserLoginSchema,
    RoleSchema,
    UserUpdateSchema,
    TokenSchema,
)
from .service import UserService # Service importálása a saját mappából

# Alap logging beállítása (ha még nincs globálisan)
# logging.basicConfig(level=logging.INFO)

@bp.route("/")
def user_index():
    return "This is The User Blueprint"


@bp.post("/registrate")
@bp.doc(tags=["user"], summary="User Registration")
@bp.input(UserRequestSchema, location="json")
@bp.output(UserResponseSchema, status_code=201)
def user_registrate(json_data):
    """Új felhasználó regisztrálása."""
    success, response_or_error = UserService.user_registrate(json_data)
    if success:
        return response_or_error
    raise HTTPError(400, message=response_or_error)


@bp.post("/login")
@bp.doc(tags=["user"], summary="User Login")
@bp.input(UserLoginSchema, location="json")
@bp.output(TokenSchema)
def user_login(json_data):
    """Felhasználó bejelentkeztetése és tokenek visszaadása."""
    success, response_or_error = UserService.user_login(json_data)
    if success:
        return response_or_error
    raise HTTPError(401, message=response_or_error)


# --- Saját felhasználói adatok lekérése ---
@bp.get("/me")
@jwt_required()
# @bp.auth_required(auth) # Maradhat kikommentelve, ha a 401-et ez okozta
@bp.output(UserResponseSchema)
@bp.doc(tags=["user"], summary="Get My Profile", description="Retrieves the profile information of the currently logged-in user.")
def get_my_profile():
    """Visszaadja a bejelentkezett felhasználó adatait."""
    current_user_id_str = get_jwt_identity()
    jwt_claims = get_jwt()

    logging.info(f"[Backend /user/me] JWT Identity (sub): {current_user_id_str}")
    logging.debug(f"[Backend /user/me] JWT Claims: {jwt_claims}")

    try:
        current_user_id = int(current_user_id_str)
    except (ValueError, TypeError) as e:
        logging.error(f"[Backend /user/me] Invalid user ID in token: {current_user_id_str} - Error: {e}")
        raise HTTPError(401, message="Érvénytelen felhasználói azonosító a tokenben.")

    user = db.session.get(User, current_user_id)
    if not user:
        logging.warning(f"[Backend /user/me] User not found with ID: {current_user_id}")
        raise HTTPError(404, "Felhasználó nem található.")

    logging.info(f"[Backend /user/me] User found and returning data for: {user.email}")
    return user


# --- Felhasználói adatok lekérése ID alapján (Admin/Recepciós számára) ---
@bp.get("/<int:uid>")
@jwt_required()
@bp.auth_required(auth) # Itt maradhat, ha Swaggerben kell az auth jelzés
@roles_required("Administrator", "Receptionist")
@bp.output(UserResponseSchema)
@bp.doc(tags=["user"], summary="Get User Details by ID", description="Retrieves details for a specific user by their ID (Admin/Receptionist access).")
def get_user_by_id(uid):
    """Visszaadja egy adott felhasználó adatait ID alapján (Admin/Recepciós)."""
    user = db.session.get(User, uid)
    if not user:
        raise HTTPError(404, 'Felhasználó nem található.')
    return user


@bp.get("/roles")
@jwt_required()
@bp.auth_required(auth)
@bp.doc(tags=["user"], summary="List All Roles")
@bp.output(RoleSchema(many=True))
def user_list_roles():
    """Listázza az összes lehetséges szerepkört."""
    success, response_or_error = UserService.user_list_roles()
    if success:
        return response_or_error
    raise HTTPError(500, message=response_or_error)


@bp.get("/roles/<int:uid>")
@jwt_required()
@bp.auth_required(auth)
@roles_required("Administrator", "Receptionist")
@bp.doc(tags=["user"], summary="List Roles for a Specific User")
@bp.output(RoleSchema(many=True))
def user_list_user_roles(uid):
    """Listázza egy adott felhasználó szerepköreit ID alapján (Admin/Recepciós)."""
    user_exists = db.session.get(User, uid)
    if not user_exists:
        raise HTTPError(404, "A megadott azonosítójú felhasználó nem található.")

    success, response_or_error = UserService.list_user_roles(uid)
    if success:
        return response_or_error
    raise HTTPError(400, message=response_or_error)


# --- Felhasználói adatok frissítése ---
@bp.put("/update/<int:uid>")
@bp.doc(tags=["user"], summary="Update User Profile")
@jwt_required() # Csak ez marad az authentikációhoz
# @bp.auth_required(auth) # <<< EZT KELL KIKOMMENTELNI/TÖRÖLNI
@bp.input(UserUpdateSchema, location="json")
@bp.output(UserResponseSchema)
def update_user(uid, json_data):
    """Felhasználói adatok frissítése (saját vagy admin által)."""
    # Logolás a függvény elején, hogy lássuk, eljut-e idáig a kérés
    logging.info(f"[Backend /user/update/{uid}] Request received. Checking permissions...")
    logging.debug(f"[Backend /user/update/{uid}] Received data: {json_data}") # DEBUG szinten a JSON adat

    try:
        current_user_id_str = get_jwt_identity()
        current_user_id = int(current_user_id_str)
        jwt_data = get_jwt()
        user_roles_from_token = jwt_data.get("roles", [])
        logging.info(f"[Backend /user/update/{uid}] Current User ID: {current_user_id}, Roles: {user_roles_from_token}")
    except (ValueError, TypeError):
        logging.error(f"[Backend /user/update/{uid}] Invalid user ID in token.")
        raise HTTPError(401, message="Érvénytelen felhasználói azonosító a tokenben.")

    # Jogosultság ellenőrzés
    if "Administrator" not in user_roles_from_token and current_user_id != uid:
        logging.warning(f"[Backend /user/update/{uid}] Permission denied. User {current_user_id} cannot update user {uid}.")
        raise HTTPError(
            403, message="Hozzáférés megtagadva: Csak a saját profilját módosíthatja."
        )
    
    logging.info(f"[Backend /user/update/{uid}] Permissions OK. Calling UserService...")
    # Ha a fenti ellenőrzésen átment (admin vagy saját profil), folytatódhat a frissítés
    success, response_or_error = UserService.update_user(uid, json_data)
    
    if success:
        logging.info(f"[Backend /user/update/{uid}] Update successful for user {uid}.")
        return response_or_error

    # Hibakezelés a service válasza alapján
    logging.error(f"[Backend /user/update/{uid}] UserService failed: {response_or_error}")
    if "User not found!" in str(response_or_error):
        raise HTTPError(404, message=str(response_or_error))
    else:
        # Minden más hiba (pl. validációs, adatbázis) 400-as kódot kapjon
        raise HTTPError(400, message=str(response_or_error))