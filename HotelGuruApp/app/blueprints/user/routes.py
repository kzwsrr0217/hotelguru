from flask import jsonify
from app.blueprints.user import bp
from app.blueprints.user.schemas import UserResponseSchema, UserRequestSchema, UserLoginSchema, RoleSchema, AddressSchema
from app.blueprints.user.service import UserService
from apiflask import HTTPError
from apiflask.fields import String, Email, Nested, Integer, List

@bp.route('/')
def index():
    return 'This is The User Blueprint'

@bp.post('/registrate')
@bp.doc(tags=["user"])
@bp.input(UserRequestSchema, location="json")
@bp.output(UserResponseSchema)
def user_registrate(json_data):
    success, response = UserService.user_registrate(json_data)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)

    

@bp.post('/login')
@bp.doc(tags=["user"])
@bp.input(UserLoginSchema, location="json")
@bp.output(UserResponseSchema)
def user_login(json_data):
    success, response = UserService.user_login(json_data)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


@bp.get('/roles')
@bp.doc(tags=["user"])
@bp.output(RoleSchema(many=True))
def user_list_roles():
    success, response = UserService.user_list_roles()
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


@bp.get('/roles/<int:uid>')
@bp.doc(tags=["user"])
@bp.output(RoleSchema(many=True))
def user_list_user_roles(uid):
    success, response = UserService.list_user_roles(uid)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


@bp.post('/address/add')
@bp.doc(tags=["user"])
@bp.input(AddressSchema, location="json")
def user_address_add(json_data):
    success, response = UserService.user_add_address(json_data)
    if success:
        return str(response), 200
    raise HTTPError(message=response, status_code=400)
