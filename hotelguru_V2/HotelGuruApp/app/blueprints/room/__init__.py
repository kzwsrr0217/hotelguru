from apiflask import APIBlueprint

bp = APIBlueprint('room', __name__, tag="room")

from app.blueprints.room import routes