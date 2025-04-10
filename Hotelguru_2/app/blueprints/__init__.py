from apiflask import APIBlueprint

bp = APIBlueprint("main", __name__, tag="default")


@bp.route("/")
def index():
    return "This is The Main Blueprint"


from app.blueprints.user import bp as bp_user

bp.register_blueprint(bp_user, url_prefix="/user")

from app.blueprints.room import bp as bp_room

bp.register_blueprint(bp_room, url_prefix="/room")

from app.blueprints.service import bp as bp_service

bp.register_blueprint(bp_service, url_prefix="/service")

from app.blueprints.reservation import bp as bp_reservation

bp.register_blueprint(bp_reservation, url_prefix="/reservation")

from app.blueprints.receptionist import bp as bp_receptionist

bp.register_blueprint(bp_receptionist, url_prefix="/receptionist")

from app.blueprints.admin import bp as bp_admin

bp.register_blueprint(bp_admin, url_prefix="/admin")

from app.blueprints.invoice import bp as bp_invoice

bp.register_blueprint(bp_invoice, url_prefix="/invoice")

from app.models import *
