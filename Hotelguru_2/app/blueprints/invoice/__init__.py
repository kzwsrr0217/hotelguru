# app/blueprints/invoice/__init__.py
from apiflask import APIBlueprint

# bp = APIBlueprint('invoice', __name__, tag="Invoice") # <<< Régi sor
bp = APIBlueprint(
    "invoice", __name__, template_folder="templates", tag="Invoice"
)  # <<< Új sor

from app.blueprints.invoice import routes
