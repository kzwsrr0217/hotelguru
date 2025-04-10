from app.blueprints.service import bp
from app.blueprints.service.schemas import (
    ServiceListSchema,
    ServiceRequestSchema,
    ServiceResponseSchema,
    ServiceUpdateSchema,
)
from app.blueprints.service.service import ServiceService

from apiflask.fields import String, Integer
from apiflask import HTTPError
from flask_jwt_extended import jwt_required  # JWT védelemhez
from app.utils.decorators import roles_required  # Szerepkör ellenőrzéshez
from app import auth  # auth importálása a JWT-hez


@bp.route("/")
def index():
    return "This is The Service Blueprint"


@bp.get("/list")
@bp.output(ServiceListSchema(many=True))
def service_list_all():
    success, response = ServiceService.service_list_all()
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


@bp.get("/list/<int:sid>")
@bp.output(ServiceListSchema)
def service_by_id(sid):
    success, response = ServiceService.service_by_id(sid)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


@bp.post("/add")
@jwt_required()  # JWT védelemhez
@roles_required("Administrator")  # Csak admin jogosultságú felhasználók férhetnek hozzá
#@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@bp.input(ServiceRequestSchema, location="json")
@bp.output(ServiceResponseSchema, status_code=201)
def service_add_new(json_data):
    success, response = ServiceService.service_add(json_data)
    if success:
        return response, 201
    raise HTTPError(message=response, status_code=400)


@bp.put("/update/<int:sid>")
@jwt_required()  # JWT védelemhez
@bp.auth_required(auth)  # Jelzi a Swaggernek, hogy auth kell
@roles_required("Administrator")  # Csak admin jogosultságú felhasználók férhetnek hozzá
@bp.input(ServiceUpdateSchema, location="json")
@bp.output(ServiceResponseSchema)
def service_update(sid, json_data):
    success, response = ServiceService.service_update(sid, json_data)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


# @bp.delete('/delete/<int:fid>')
# def service_delete(sid):
#     success, response = ServiceService.service_delete(sid)
#     if success:
#         return response, 200
#     raise HTTPError(message=response, status_code=400)
