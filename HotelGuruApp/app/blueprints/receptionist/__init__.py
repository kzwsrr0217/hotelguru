from apiflask import APIBlueprint

bp = APIBlueprint('receptionist', __name__, tag="receptionist")

from app.blueprints.receptionist import routes
