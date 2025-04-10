# tests/conftest.py
import pytest
from app import create_app, db # Fontos: az app factory és a db objektum
from config import Config     # Az alap konfiguráció

# --- Teszt Konfiguráció ---
class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    DEBUG = False
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret-key'
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}"
        f"@localhost:3307/{Config.DB_NAME}?charset=utf8mb4")


# --- Pytest Fixture-ök ---

@pytest.fixture(scope='session')
def app():
    # ... (ez a fixture változatlan) ...
    _app = create_app(config_class=TestConfig)
    ctx = _app.app_context()
    ctx.push()
    yield _app
    ctx.pop()

@pytest.fixture(scope='function') # Minden tesztfüggvényhez új kliens
def client(app):
    """Létrehoz egy teszt klienst az API hívásokhoz."""
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app): # Függ az app fixture-től
    """
    Biztosítja a Flask-SQLAlchemy sessiont egy teszthez,
    egy beágyazott tranzakcióba csomagolva, amit a teszt végén visszavon (rollback).
    Feltételezi, hogy az adatbázis séma már létezik.
    """
    with app.app_context(): # Szükséges a db.session eléréséhez
        # Beágyazott tranzakció indítása. Ez lehetővé teszi, hogy az alkalmazáskód
        # akár db.session.commit()-ot is hívjon a kérésen belül, de a külső
        # teszt tranzakciót ettől még vissza lehet vonni.
        db.session.begin_nested()

        print("\n[DB Fixture] Nested Transaction started.") # Debug üzenet

        # Az eredeti Flask-SQLAlchemy session objektum átadása
        # A tesztek ezt használhatják setup/assertion célokra, ha kell,
        # de a 'client'-en keresztül hívott alkalmazáskód automatikusan ezt használja.
        yield db.session

        # --- Teardown (a yield után fut le) ---
        # A beágyazott tranzakció visszavonása
        db.session.rollback()
        print("\n[DB Fixture] Nested Transaction rolled back.")

        # A session tényleges eltávolítását (scoped session esetén)
        # általában a Flask-SQLAlchemy kezeli a kérés/kontextus végén.
        # db.session.remove() # Valószínűleg nem szükséges itt expliciten


# --- Segéd Fixture (Opcionális, de hasznos) ---

@pytest.fixture(scope='function')
def admin_auth_headers(client):
    """Bejelentkezteti az admin felhasználót és visszaadja az auth headert."""
    # Feltételezi, hogy az 'admin@hotel.test' / 'adminpass' felhasználó létezik (init_db.py)
    login_data = {
        'email': 'admin@hotel.test',
        'password': 'adminpass'
    }
    response = client.post('/api/user/login', json=login_data)
    if response.status_code != 200:
        pytest.fail("Admin login failed during test setup.") # Teszt meghiúsítása, ha a login nem megy

    access_token = response.get_json()['access_token']
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    return headers

@pytest.fixture(scope='function')
def guest_auth_headers(client):
    """Bejelentkezteti az 'guest1' felhasználót és visszaadja az auth headert."""
    login_data = {
        'email': 'guest1@example.com',
        'password': 'guest1pass'
    }
    response = client.post('/api/user/login', json=login_data)
    if response.status_code != 200:
        pytest.fail("Guest login failed during test setup.")

    access_token = response.get_json()['access_token']
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    return headers