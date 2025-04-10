from app.extensions import db
from app.blueprints.user.schemas import UserResponseSchema, RoleSchema
from app.models.user import User
from app.models.address import Address
from app.models.role import Role
import logging
from sqlalchemy import select
from flask_jwt_extended import create_access_token, create_refresh_token


class UserService:

    @staticmethod
    def user_registrate(request):
        try:
            if db.session.execute(
                select(User).filter_by(email=request["email"])
            ).scalar_one_or_none():
                return False, "E-mail already exist!"

            request["address"] = Address(**request["address"])
            user = User(**request)
            user.set_password(user.password)
            user.roles.append(
                db.session.execute(select(Role).filter_by(name="Guest")).scalar_one()
            )
            db.session.add(user)
            db.session.commit()
        except KeyError as ke:
            return False, f"Missing required field: {str(ke)}"
        except ValueError as ve:
            return False, f"Invalid data format: {str(ve)}"
        except Exception as ex:
            return False, f"Registration error: {str(ex)}"
        return True, UserResponseSchema().dump(user)

    @staticmethod
    def user_login(request):
        try:
            user = db.session.execute(
                select(User).filter_by(email=request["email"])
            ).scalar_one_or_none()
            if not user or not user.check_password(request["password"]):
                return False, "Incorrect e-mail or password!"

            # --- Token Generálás (Módosítva) ---
            user_identity = str(user.id)  # <<< ID átalakítása stringgé!
            access_token = create_access_token(identity=user_identity)
            refresh_token = create_refresh_token(identity=user_identity)
            # --- VÉGE Token Generálás (Módosítva) ---

        except Exception as ex:
            logging.exception(f"Login error for {request.get('email', 'N/A')}: {ex}")
            return False, "Incorrect Login data or Server Error!"

        return True, {"access_token": access_token, "refresh_token": refresh_token}

    @staticmethod
    def user_list_roles():
        roles = db.session.query(Role).all()
        return True, RoleSchema().dump(obj=roles, many=True)

    @staticmethod
    def list_user_roles(uid):
        user = db.session.get(User, uid)
        if user is None:
            return False, "User not found!"
        return True, RoleSchema().dump(obj=user.roles, many=True)

    @staticmethod
    def update_user(uid, request):
        try:
            user = db.session.get(User, uid)
            if user:
                if "address" in request:
                    address_data = request["address"]
                    if user.address:
                        user.address.street = address_data.get(
                            "street", user.address.street
                        )
                        user.address.city = address_data.get("city", user.address.city)
                        user.address.postalcode = address_data.get(
                            "postalcode", user.address.postalcode
                        )
                    else:
                        user.address = Address(**address_data)

                if "email" in request:
                    user.email = request["email"]

                if "phone_number" in request:
                    user.phone = request["phone_number"]

                if "password" in request:
                    user.set_password(user.password)

                db.session.commit()
                return True, UserResponseSchema().dump(user)
            return False, "User not found!"

        except Exception as ex:
            print(ex)
            return False, "User_update() error!"
