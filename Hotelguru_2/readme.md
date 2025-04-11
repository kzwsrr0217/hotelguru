# HotelGuru API Backend

Ez a projekt a HotelGuru szállodamenedzsment rendszer backend API-ját tartalmazza. Felelős a felhasználók, szobák, szolgáltatások, foglalások és számlák kezeléséért, valamint az adatok tárolásáért és a jogosultságok kezeléséért. A frontend alkalmazás ([HotelGuru Frontend](#frontend)) ezzel az API-val kommunikál.

## Technológiai Stack

* **Programozási nyelv:** Python 3.9+
* **Web Keretrendszer:** Flask & APIFlask (REST API-hoz és automatikus Swagger dokumentációhoz)
* **Adatbázis ORM:** SQLAlchemy
* **Adatbázis Migráció:** Flask-Migrate (Alembic)
* **Authentikáció:** Flask-JWT-Extended (JWT token alapú, szerepkörökkel)
* **Adatbázis:** MySQL (Dockerizálva)
* **Konténerizáció:** Docker, Docker Compose
* **Szerializáció/Validáció:** Marshmallow (APIFlask integrációval)
* **PDF Generálás:** WeasyPrint (számlákhoz)
* **CORS Kezelés:** Flask-Cors
* **Konfiguráció:** Környezeti változók, `.env` (helyi futtatáshoz), `python-dotenv`
* **Tesztelés:** Pytest, Pytest-Flask
* **Kód Formázás/Linting:** Black, Flake8

## Előfeltételek

* **Git:** A kód letöltéséhez ([https://git-scm.com/](https://git-scm.com/))
* **Docker & Docker Compose:** A konténerizált futtatáshoz (ajánlott) ([https://www.docker.com/get-started](https://www.docker.com/get-started))
* **(Opcionális, Docker nélküli futtatáshoz) Python 3.9+ és pip**
* **(Opcionális) MySQL Kliens:** Adatbázis-kezelő eszköz (pl. MySQL Workbench, DBeaver, HeidiSQL) az adatbázis tartalmának közvetlen ellenőrzéséhez.

## Telepítés és Futtatás

### 1. Docker Compose Használatával (Ajánlott)

Ez a módszer biztosítja a konzisztens fejlesztői és futtatási környezetet.

1.  **Repository Klónozása:** (Ha még nem történt meg)
    ```bash
    git clone -b v2-docker https://github.com/kzwsrr0217/hotelguru.git
    vagy
    git clone https://github.com/kzwsrr0217/hotelguru.git
    cd hotelguru
    git branch -r
    git checkout v2-docker
    ```

2.  **Konténerek Építése és Indítása:**
    Ez a parancs megépíti a Docker image-eket, létrehozza a hálózatot/köteteket, és elindítja a Flask (`app`) és MySQL (`db`) konténereket a háttérben (`-d`).
    ```bash
    docker-compose up --build -d
    ```
    Várj egy kicsit (akár 1-2 percet is), amíg a MySQL adatbázis (`db` konténer) elindul és "egészséges" állapotba kerül. Az `app` konténer ezt automatikusan megvárja a `depends_on` és `healthcheck` beállítások miatt. A folyamatot a `docker-compose logs -f` paranccsal követheted.

3.  **Adatbázis Inicializálása (Konténeren Belül):**
    Az első indításkor, vagy ha törölted az adatbázis kötetet (`mysql_data`), inicializálni kell az adatbázist az `app` konténeren belül. Futtasd ezeket a parancsokat a projekt gyökérkönyvtárából (`Hotelguru_2` mappa):

    * **Adatbázisséma Létrehozása/Frissítése:** Lefuttatja a meglévő Alembic migráció(ka)t a `migrations/` mappából.
        ```bash
        docker-compose exec app flask db upgrade
        ```
    * **Kezdeti Adatok Betöltése (Seed):** Feltölti az adatbázist alapértelmezett szerepkörökkel, szobatípusokkal, admin/recepciós/vendég felhasználókkal, szobákkal és néhány minta foglalással/számlával. **Figyelem: Ha már vannak adataid, ez felülírhatja vagy hibát okozhat! Csak tiszta adatbázis esetén vagy újrakezdéskor futtasd.**
        ```bash
        docker-compose exec app python init_db.py
        ```
    * **(Később, Modell Változás Esetén) Új Migráció Létrehozása:** Ha a jövőben módosítod a SQLAlchemy modelleket (`app/models/`), futtasd *először* ezt, majd az `upgrade`-et:
        ```bash
        # 1. Új migrációs fájl generálása
        docker-compose exec app flask db migrate -m "Rövid leírás a változásról"
        # 2. Az új migráció alkalmazása az adatbázisra
        docker-compose exec app flask db upgrade
        ```

4.  **Alkalmazás Elérése:**
    * Az API elérhető: `http://localhost:8888/api`
    * A Swagger UI dokumentáció: `http://localhost:8888/swagger`

5.  **Adatbázis Közvetlen Elérése (Opcionális):**
    Használj egy MySQL klienst a csatlakozáshoz:
    * **Host:** `localhost`
    * **Port:** `3307` (Ezt állítottuk be a `docker-compose.yml`-ben!)
    * **Felhasználó:** `hotel_user` (vagy amit a `docker-compose.yml`-ben beállítottál)
    * **Jelszó:** `hotel_password` (vagy amit a `docker-compose.yml`-ben beállítottál)
    * **Adatbázis/Séma:** `hotel_db` (vagy amit a `docker-compose.yml`-ben beállítottál)

### 2. Docker Nélkül (Helyi Fejlesztés)

Ez a módszer több kézi beállítást igényel.

1.  **Repository Klónozása:** (Lásd fent)
2.  **Helyi MySQL Beállítása:** Telepíts és indíts el egy MySQL szervert. Hozz létre egy adatbázist (pl. `hotel_db_local`) és egy felhasználót/jelszót hozzá.
3.  **Virtuális Környezet:**
    ```bash
    python -m venv venv # Vagy env1, stb.
    # Aktiválás (Windows):
    .\venv\Scripts\activate
    # Aktiválás (Linux/macOS):
    source venv/bin/activate
    ```
4.  **Függőségek Telepítése:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Győződj meg róla, hogy a `requirements.txt` tartalmazza a `python-dotenv` és `Flask-Cors` csomagokat is!)*
5.  **Környezeti Változók (`.env` fájl):**
    * Hozd létre a projekt gyökerében (`Hotelguru_2`) egy `.env` fájlt.
    * Állítsd be a **helyi** adatbázis adatait és a titkos kulcsokat:
        ```dotenv
        # Hotelguru_2/.env fájl HELYI FUTTATÁSHOZ
        SECRET_KEY='generálj_egy_erős_lokális_kulcsot'
        JWT_SECRET_KEY='generálj_egy_másik_erős_lokális_kulcsot'

        # HELYI adatbázis adatai!
        DB_USER=a_helyi_mysql_usered
        DB_PASSWORD=a_helyi_mysql_jelszavad
        DB_HOST=localhost # Vagy 127.0.0.1
        DB_PORT=3306 # Az alapértelmezett MySQL port
        DB_NAME=hotel_db_local # A helyileg létrehozott adatbázis neve

        # Opcionális: Helyettesítheti a fenti DB_* változókat
        # SQLALCHEMY_DATABASE_URI='mysql+pymysql://user:pass@localhost:3306/hotel_db_local'

        FLASK_DEBUG=1
        FLASK_APP=run_app:create_app() # Flask CLI-nek segít megtalálni az appot
        ```
    * **(Fontos)** Győződj meg róla, hogy a `.env` fájl szerepel a `.gitignore` fájlban!
6.  **Adatbázis Inicializálása (Helyi):**
    * Aktivált virtuális környezetben (`(venv)`) futtasd:
        ```bash
        flask db upgrade
        python init_db.py # Csak ha kezdőadatok is kellenek
        ```
    * Modell változás esetén: `flask db migrate -m "..."`, majd `flask db upgrade`.
7.  **Alkalmazás Indítása:**
    ```bash
    flask run --host=0.0.0.0 --port=8888
    ```
    * Az API elérhető: `http://localhost:8888/api`
    * Swagger UI: `http://localhost:8888/swagger`

## Konfiguráció

Az alkalmazás a `config.py`-ban definiált `Config` osztályt használja. Ez a következőképpen tölti be a beállításokat:

1.  Megpróbálja beolvasni a környezeti változókat (`os.environ.get(...)`). Docker Compose esetén ezeket a `docker-compose.yml` `environment` szekciója adja át. Helyi futtatásnál a rendszer környezeti változói vagy a `python-dotenv` által betöltött `.env` fájl értékei lehetnek.
2.  Ha egy környezeti változó nincs beállítva, a `config.py`-ban megadott alapértelmezett értéket használja (pl. `DB_HOST='db'`, `DB_USER='hotel_user'`).
3.  A `SQLALCHEMY_DATABASE_URI` vagy közvetlenül beállítható környezeti változóként (`DATABASE_URI`), vagy a `DB_*` változókból automatikusan összeállításra kerül.

**Fontos Kulcsok:**

* `SECRET_KEY`: Flask alkalmazás biztonsági kulcsa.
* `JWT_SECRET_KEY`: JWT tokenek aláírásához használt kulcs.
* `SQLALCHEMY_DATABASE_URI`: Adatbázis kapcsolati string.

**Éles környezetben a titkos kulcsokat SOHA ne tárold a kódban vagy a `docker-compose.yml`-ben!** Használj biztonságosabb módszereket (pl. Docker secrets, környezeti változók a futtató platformon).

## API Dokumentáció

Az API végpontok részletes, interaktív dokumentációja elérhető az automatikusan generált **Swagger UI** felületen az alkalmazás indítása után:

**`http://localhost:8888/swagger`**

Itt láthatod az összes elérhető végpontot, azok paramétereit, kérés/válasz sémáit, és ki is próbálhatod őket.

**Megjegyzés a Swagger Authorize funkciójáról:** A `@jwt_required` és az APIFlask `@bp.auth_required` dekorátorai közötti konfliktus miatt néhány védett végpontról eltávolítottuk az `@bp.auth_required` dekorátort. Emiatt előfordulhat, hogy a Swagger UI "Authorize" gombjával beállított Bearer token nem kerül automatikusan hozzáadásra ezekhez a végpontokhoz a "Try it out" funkció használatakor. Ilyenkor manuálisan kell megadni az `Authorization: Bearer <token>` fejlécet.

## API Végpontok (Összefoglaló)

Az API a `/api` prefix alatt érhető el. Főbb modulok (Blueprintek):

* `/api/user`: Felhasználói műveletek (regisztráció, login, profil, szerepkörök).
* `/api/room`: Szobákkal kapcsolatos publikus műveletek (elérhető szobák listázása dátummal/nélküle, szoba részletei).
* `/api/service`: Szolgáltatások listázása, kezelése (Admin).
* `/api/reservation`: Foglalási műveletek (új foglalás, lemondás, saját foglalások, visszaigazolás).
* `/api/receptionist`: Recepciós műveletek (összes foglalás, check-in/out, státusz módosítás, szolgáltatás hozzáadása).
* `/api/admin`: Adminisztrátori műveletek (szoba CRUD).
* `/api/invoice`: Számlázással kapcsolatos műveletek (PDF generálás/letöltés).

## Projekt Struktúra (Backend)

* `run_app.py`: Alkalmazás indítási pontja.
* `config.py`: Konfigurációs beállítások.
* `requirements.txt`: Python függőségek.
* `init_db.py`: Adatbázis inicializáló (seed) szkript.
* `docker-compose.yml`: Docker Compose konfiguráció.
* `Dockerfile`: Docker image építési utasítások.
* `app/`: Fő alkalmazás könyvtár.
    * `__init__.py`: Alkalmazás factory (`create_app`).
    * `extensions.py`: Flask kiterjesztések inicializálása (`db`).
    * `models/`: SQLAlchemy adatbázis modellek és kapcsolótáblák.
    * `blueprints/`: Funkcionális modulok (user, room, admin stb.).
        * `*/__init__.py`: Blueprint inicializálása.
        * `*/routes.py`: API végpontok definíciói (Flask route-ok, APIFlask dekorátorok).
        * `*/schemas.py`: Marshmallow sémák (adat validáció/szerializáció).
        * `*/service.py`: Üzleti logika rétege (adatbázis műveletek, ellenőrzések).
    * `utils/`: Segédprogramok (pl. `@roles_required` dekorátor).
* `migrations/`: Alembic adatbázis migrációs fájlok.
* `tests/`: Pytest tesztek (API és unit tesztek).
    * `conftest.py`: Pytest fixture-ök.

## Tesztelés

* A projekt tartalmaz API teszteket a `tests/` könyvtárban `pytest` használatával.
* Futtatás (aktivált virtuális környezetben vagy Dockerben): `python -m pytest -v`
* A tesztek jelenleg a fejlesztői adatbázishoz kapcsolódnak, de minden teszt saját tranzakcióban fut, amit a végén visszavonnak (rollback), így nem hagynak szemetet maguk után (`conftest.py`).

## Leállítás (Docker)

A Docker konténerek leállításához és eltávolításához:

```bash
docker-compose down
Ez a parancs nem törli a mysql_data nevű Docker kötetet, így az adatbázis adatai megmaradnak. Ha teljesen tiszta adatbázissal akarsz indulni legközelebb, futtasd a docker volume rm hotelguru2_mysql_data (vagy a pontos kötetnevet, amit a docker volume ls mutat) parancsot a docker-compose down után.
