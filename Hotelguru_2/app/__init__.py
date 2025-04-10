from config import Config
from flask import Flask
from apiflask import APIFlask
from config import Config
from app.extensions import db
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, get_jwt_identity
from app.models.user import User
from apiflask.security import HTTPTokenAuth 
from app.models.role import Role
from app.models import *
from flask_cors import CORS


jwt = JWTManager()
auth = HTTPTokenAuth(scheme='Bearer') 

# Ez a callback lefut minden alkalommal, amikor create_access_token-t hívunk
@jwt.additional_claims_loader
def add_roles_to_access_token(identity):
    # Az 'identity' itt a felhasználó ID-ja (stringként, ahogy a loginban beállítottuk)
    try:
        user_id = int(identity)  # Visszaalakítjuk int-té a lekérdezéshez
        user = db.session.get(User, user_id)  # User lekérdezése ID alapján
        if user and user.roles:
            # Ha van user és vannak szerepkörei, adjuk hozzá a listát a tokenhez
            user_roles = [role.name for role in user.roles]  # Szerepkörnevek listája
            return {"roles": user_roles}
        else:
            # Ha nincs user vagy nincsenek szerepkörei
            return {"roles": []}
    except (ValueError, TypeError):
        # Ha az identity nem konvertálható int-té
        return {"roles": []}
    except Exception as e:
        # Egyéb hiba esetén (pl. DB hiba) - logolhatnánk
        print(f"Error adding roles to token: {e}")  # Ideiglenes print
        return {"roles": []}  # Üres lista hiba esetén



def create_app(config_class=Config):
    # app = Flask(__name__)
    # app = Flask(__name__)
    app = APIFlask(
        __name__, json_errors=True, title="Hotelguru API", docs_path="/swagger"
    )
 # --- CORS Inicializálása ---
    # Fejlesztéshez :
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    # Éles környezetben:
    # CORS(app, resources={r"/api/*": {"origins": "https://a-frontend-valodi-domainje.hu"}})
    # --------------------------    app.config.from_object(config_class)
    app.config.from_object(config_class)
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI

    app.config["SECURITY_SCHEMES"] = {
        "BearerAuth": {  # Ez egy általad választott név a sémának
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",  # Leírja, hogy ez egy JWT token
        }
    }
    # Initialize Flask extensions here
    print(f"[DEBUG] app.config['SQLALCHEMY_DATABASE_URI'] before db.init_app: {app.config.get('SQLALCHEMY_DATABASE_URI')}") # <<< EZT A SORT SZÚRD BE

    db.init_app(app)
    jwt.init_app(app)
    # from flask_migrate import Migrate -az elejére raktam
    migrate = Migrate(app, db, render_as_batch=True)

    # Register blueprints here
    # from app.main import bp as main_bp
    # app.register_blueprint(main_bp)
    from app.blueprints import bp as bp_default

    app.register_blueprint(bp_default, url_prefix="/api")

    return app
