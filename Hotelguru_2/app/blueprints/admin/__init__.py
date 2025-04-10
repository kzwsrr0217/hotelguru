print("DEBUG: Running admin blueprint __init__.py")
from apiflask import APIBlueprint

bp = APIBlueprint("admin", __name__, tag="Admin")

from app.blueprints.admin import routes
