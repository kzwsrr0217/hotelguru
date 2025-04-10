from apiflask import APIBlueprint

bp = APIBlueprint("receptionist", __name__, tag="Receptionist")

from app.blueprints.receptionist import routes
