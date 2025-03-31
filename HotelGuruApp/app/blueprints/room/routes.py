from app.blueprints.room import bp
from app.blueprints.room.schemas import RoomListSchema, RoomRequestSchema, RoomResponseSchema
from app.blueprints.room.service import RoomService
from apiflask.fields import String, Integer
from apiflask import HTTPError

@bp.route('/')
def index():
    return 'This is The Room Blueprint'

@bp.get('/list/')
@bp.output(RoomListSchema(many = True))
def room_list_all():
    success, response = RoomService.room_list_all()
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)

@bp.get('/list/<int:rid>')
@bp.output(RoomListSchema(many = True))
def room_list_type(rid):
    success, response = RoomService.room_list_type(rid)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


@bp.post('/add')
@bp.input(RoomRequestSchema, location="json")
@bp.output(RoomResponseSchema)
def room_add_new(json_data):
    success, response = RoomService.room_add(json_data)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


@bp.put('/update/<int:rid>')
@bp.input(RoomRequestSchema, location="json")
@bp.output(RoomResponseSchema)
def room_update(rid, json_data):
    success, response = RoomService.room_update(rid, json_data)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)
