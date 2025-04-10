# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

print("--- Loading Config ---") # <<< Debug print

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "my secret key"
    JWT_SECRET_KEY = (
        os.environ.get("JWT_SECRET_KEY") or "my-super-secret-jwt-key-change-me"
    )

    DB_USER = os.environ.get("DB_USER") or "hotel_user"
    DB_PASSWORD = os.environ.get("DB_PASSWORD") or "hotel_password"
    DB_HOST = (
        os.environ.get("DB_HOST") or "db"
    )
    DB_PORT = os.environ.get("DB_PORT") or "3306"
    DB_NAME = os.environ.get("DB_NAME") or "hotel_db"

    # <<< Debug print sorok Kezdete >>>
    print(f"[Config] DB_USER read as: {DB_USER}")
    print(f"[Config] DB_PASSWORD read as: {'*' * len(DB_PASSWORD) if DB_PASSWORD else 'None'}")
    print(f"[Config] DB_HOST read as: {DB_HOST}")
    print(f"[Config] DB_PORT read as: {DB_PORT}")
    print(f"[Config] DB_NAME read as: {DB_NAME}")
    print(f"[Config] DATABASE_URI from env: {os.environ.get('DATABASE_URI')}")
    # <<< Debug print sorok Vége >>>

    # Kapcsolati string összeállítása
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URI")
        or f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    # ---------------------------------------------

    # <<< Debug print sor >>>
    print(f"[Config] Final SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")
    # <<< Debug print sor vége >>>

    SQLALCHEMY_TRACK_MODIFICATIONS = False

print("--- Config Loaded ---") # <<< Debug print