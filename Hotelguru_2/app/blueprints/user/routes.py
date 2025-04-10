from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt  # JWT védelemhez
from app.utils.decorators import roles_required  # Szerepkör ellenőrzéshez
from app import auth  # auth importálása a JWT-hez
from flask import jsonify
from app.blueprints.user import bp
from app.blueprints.user.schemas import (
    UserResponseSchema,
    UserRequestSchema,
    UserLoginSchema,
    RoleSchema,
    AddressSchema,
    UserUpdateSchema,
    TokenSchema,
)
from app.blueprints.user.service import UserService
from apiflask import HTTPError
from apiflask.fields import String, Email, Nested, Integer, List


@bp.route("/")
def user_index():
    return "This is The User Blueprint"


@bp.post("/registrate")
@bp.doc(tags=["user"])
@bp.input(UserRequestSchema, location="json")
@bp.output(UserResponseSchema)
def user_registrate(json_data):
    success, response = UserService.user_registrate(json_data)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


@bp.post("/login")
@bp.doc(tags=["user"])
@bp.input(UserLoginSchema, location="json")
@bp.output(TokenSchema)
def user_login(json_data):
    success, response = UserService.user_login(json_data)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=401)


@bp.get("/roles")
@jwt_required()  # JWT védelemhez
@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@bp.doc(tags=["user"])
@bp.output(RoleSchema(many=True))
def user_list_roles():
    success, response = UserService.user_list_roles()
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


@bp.get("/roles/<int:uid>")
@jwt_required()  # JWT védelemhez
@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@bp.doc(tags=["user"])
@bp.output(RoleSchema(many=True))
def user_list_user_roles(uid):
    success, response = UserService.list_user_roles(uid)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


@bp.put("/update/<int:uid>")
@bp.doc(tags=["user"])
@jwt_required()  # <<< JWT token szükséges
@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@bp.input(UserUpdateSchema, location="json")
@bp.output(UserResponseSchema)
def update_user(uid, json_data):
    """Felhasználói adatok frissítése (saját vagy admin által)."""
    # --- Jogosultság ellenőrzés kezdete ---
    try:
        current_user_id = int(get_jwt_identity())  # Bejelentkezett felhasználó ID-ja
        jwt_data = get_jwt()  # Teljes JWT payload lekérése
        user_roles = jwt_data.get("roles", [])  # Felhasználó szerepköreinek lekérése
    except (ValueError, TypeError):
        # Ha az identity nem konvertálható int-té, az hiba
        raise HTTPError(401, message="Érvénytelen felhasználói azonosító a tokenben.")

    # Ellenőrzés: A felhasználó nem adminisztrátor ÉS nem a saját profilját próbálja módosítani?
    if "Administrator" not in user_roles and current_user_id != uid:
        raise HTTPError(
            403, message="Hozzáférés megtagadva: Csak a saját profilját módosíthatja."
        )
    # --- Jogosultság ellenőrzés vége ---

    # Ha a fenti ellenőrzésen átment (admin vagy saját profil), folytatódhat a frissítés
    success, response = UserService.update_user(uid, json_data)
    if success:
        return response, 200
    # A service réteg adhat vissza 404-et (User not found) vagy 400-at (egyéb hiba)
    if "User not found!" in str(response):
        raise HTTPError(404, message=str(response))
    else:
        raise HTTPError(400, message=str(response))
