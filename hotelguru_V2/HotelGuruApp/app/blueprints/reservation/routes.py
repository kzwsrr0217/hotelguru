from app.blueprints.reservation import bp
from app.blueprints.reservation.schemas import ReservationListSchema, ReservationRequestSchema, ReservationResponseSchema, ReservationUpdateSchema
from app.blueprints.reservation.service import ReservationService
from apiflask.fields import String, Integer
from apiflask import HTTPError

@bp.route('/')
def index():
    return 'This is The Reservation Blueprint'

@bp.get('/list/')
@bp.output(ReservationListSchema(many = True))
def reservation_list_all():
    success, response = ReservationService.reservation_list_all()
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)

@bp.get('/list_by_room/<int:rid>')
@bp.output(ReservationListSchema(many = True))
def reservation_list_by_room(rid):
    success, response = ReservationService.serach_reservation_by_room(rid)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)

@bp.get('/search_by_id/<int:rid>')
@bp.output(ReservationListSchema)
def reservation_search_by_id(rid):
    success, response = ReservationService.serach_reservation_by_id(rid)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)

@bp.get('/list_by_user/<int:uid>')
@bp.output(ReservationListSchema(many = True))
def reservation_list_by_user(uid):
    success, response = ReservationService.serach_reservation_by_user(uid)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


@bp.post('/add')
@bp.input(ReservationRequestSchema, location="json")
def reservation_add(json_data):
    success, response = ReservationService.add_reservation(json_data)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


@bp.put('/update/<int:rid>')
@bp.input(ReservationUpdateSchema, location="json")
@bp.output(ReservationResponseSchema)
def reservation_update(rid, json_data):
    success, response = ReservationService.update_reservation(rid, json_data)
    if success:
        return response, 200
    raise HTTPError(message=response, status_code=400)


# @bp.delete('/delete/<int:rid>')
# def delete_reservation(rid):
#     success, response = ReservationService.delete_reservation(rid)
#     if success:
#         return response, 200
#     raise HTTPError(message=response, status_code=400)