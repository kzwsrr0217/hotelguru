# HotelGuru Teljes Projekt

Ez a projekt a HotelGuru szállodamenedzsment rendszer teljes forráskódját tartalmazza, beleértve a backend API-t (Flask/Python) és a felhasználói felületet (Vue.js).

## Áttekintés

* **Backend:** Egy Flask és APIFlask alapú REST API, amely kezeli a felhasználókat, szobákat, foglalásokat, számlákat stb. SQLAlchemy-t használ az adatbázis-kezeléshez (MySQL) és JWT-t az authentikációhoz. Dockerizálva fut.
* **Frontend:** Egy Vue.js 3 és Vuetify 3 alapú SPA (Single Page Application), amely a backend API-val kommunikál a felhasználói műveletek elvégzéséhez. Vite build eszközt használ.

## Technológiai Stack

### Backend (`Hotelguru_2` mappa)

* **Nyelv/Keretrendszer:** Python 3.9+, Flask, APIFlask
* **Adatbázis:** MySQL (Dockerben), SQLAlchemy (ORM), Flask-Migrate (Migráció)
* **API & Doku:** REST, Swagger UI (automatikus)
* **Authentikáció:** JWT (Flask-JWT-Extended)
* **Egyéb:** Marshmallow, WeasyPrint, Flask-Cors, Black, Flake8, Pytest

### Frontend (`hotelguru-frontend` mappa)

* **Keretrendszer:** Vue.js 3 (Composition API)
* **Build Eszköz:** Vite
* **UI Könyvtár:** Vuetify 3
* **Állapotkezelés & Routing:** Pinia, Vue Router
* **API Hívások:** Axios
* **Egyéb:** ESLint, Prettier, @mdi/font

## Előfeltételek

* **Git:** A kód letöltéséhez ([https://git-scm.com/](https://git-scm.com/))
* **Docker & Docker Compose:** A konténerizált futtatáshoz (ajánlott és az itt leírt elsődleges módszer) ([https://www.docker.com/get-started](https://www.docker.com/get-started)). Docker kezeli a Python, Node.js és MySQL környezetek létrehozását.

## Telepítés és Futtatás Docker Compose Használatával (Ajánlott Módszer)

Ez a módszer biztosítja a konzisztens fejlesztői és futtatási környezetet mind a backend, mind a frontend számára.

1.  **Repository Klónozása:** (Ha még nem történt meg)
    ```bash
    git clone <repository_url>
    cd <repository_root_folder>
    ```

2.  **Backend Könyvtárba Lépés:** A `docker-compose.yml` fájl a backend mappában (`Hotelguru_2`) található, innen kell indítani a parancsokat.
    ```bash
    cd Hotelguru_2
    ```

3.  **Konténerek Építése és Indítása:**
    Ez a parancs megépíti a backend (`app`) és frontend (`frontend`) Docker image-eket (ha még nem léteznek, vagy ha a `Dockerfile`-ok változtak), létrehozza a hálózatot/köteteket, és elindítja a `app`, `frontend` és `db` (MySQL) konténereket a háttérben (`-d`).
    ```bash
    docker-compose up --build -d
    ```
    Várj egy kicsit (akár 1-2 percet is), amíg a MySQL adatbázis (`db` konténer) elindul és "egészséges" állapotba kerül. Az `app` konténer ezt automatikusan megvárja a `depends_on` és `healthcheck` beállítások miatt. A `frontend` konténer is elindul. A folyamatot a `docker-compose logs -f` paranccsal követheted.

4.  **Backend Adatbázis Inicializálása (Konténeren Belül):**
    Az első indításkor, vagy ha törölted az adatbázis kötetet (`mysql_data`), inicializálni kell az adatbázist az `app` konténeren belül. Futtasd ezeket a parancsokat a `Hotelguru_2` mappából:

    * **Adatbázisséma Létrehozása/Frissítése:** Lefuttatja a meglévő Alembic migráció(ka)t.
        ```bash
        docker-compose exec app flask db upgrade
        ```
    * **Kezdeti Adatok Betöltése (Seed):** Feltölti az adatbázist alapértelmezett adatokkal (szerepkörök, felhasználók, szobák stb.). **Figyelem: Csak tiszta adatbázis esetén vagy újrakezdéskor futtasd, mert felülírhat adatokat!**
        ```bash
        docker-compose exec app python init_db.py
        ```

5.  **Konfiguráció Ellenőrzése (`docker-compose.yml`):**
    A sikeres működéshez fontosak az alábbi beállítások a `docker-compose.yml`-ben (már helyesen kellene beállítva lenniük az előző lépések alapján):
    * **Frontend API Cím:** A `frontend` szolgáltatás `environment` szekciójában a `VITE_API_BASE_URL`-nek **`http://localhost:8888/api`**-ra kell mutatnia. Ez azért fontos, mert a frontend kód a **böngészőben** fut, és a böngésző a host gépen keresztül, a backend `8888`-as portjára kiadott átirányításon át éri el az API-t.
        ```yaml
        services:
          # ...
          frontend:
            # ...
            environment:
              - NODE_ENV=development
              - VITE_API_BASE_URL=http://localhost:8888/api # <-- Ennek így kell lennie!
            # ...
        ```
    * **Frontend Port:** A `frontend` szolgáltatás `ports` beállítása legyen `"3000:5173"`. Ez a host gép 3000-es portját irányítja át a frontend konténer 5173-as portjára (ahol a Vite fejlesztői szerver fut).
    * **Frontend Indítási Parancs:** A `frontend` szolgáltatás `command` beállítása legyen `["npm", "run", "dev", "--", "--host"]`, hogy a Vite szerver minden hálózati címen figyeljen a konténeren belül.

6.  **Alkalmazás Elérése:**
    * **Frontend Felhasználói Felület:** `http://localhost:3000`
    * **Backend API Alap URL:** `http://localhost:8888/api`
    * **Backend Swagger UI Dokumentáció:** `http://localhost:8888/swagger`

7.  **Adatbázis Közvetlen Elérése (Opcionális):**
    Használj egy MySQL klienst a csatlakozáshoz:
    * **Host:** `localhost`
    * **Port:** `3307` (A `docker-compose.yml`-ben beállított host port!)
    * **Felhasználó:** `hotel_user` (vagy amit beállítottál)
    * **Jelszó:** `hotel_password` (vagy amit beállítottál)
    * **Adatbázis/Séma:** `hotel_db` (vagy amit beállítottál)

## Fejlesztési Folyamat

* **Backend Kód Változások:** Mivel a backend kód a `volumes: - .:/app` beállítással csatolva van, a legtöbb Python kódváltozás után a Flask fejlesztői szerver (debug módban) automatikusan újraindul az `app` konténeren belül.
* **Frontend Kód Változások:** Mivel a frontend kód (`../hotelguru-frontend:/app`) és a `node_modules` is csatolva van, a Vite fejlesztői szerver a legtöbb változást automatikusan észleli és frissíti a böngészőt (HMR).
* **Backend Modell Változások:** Ha a SQLAlchemy modelleket (`app/models/`) módosítod:
    1.  Új migrációs fájl generálása:
        ```bash
        docker-compose exec app flask db migrate -m "Rövid leírás a változásról"
        ```
    2.  Az új migráció alkalmazása az adatbázisra:
        ```bash
        docker-compose exec app flask db upgrade
        ```
* **Frontend Kódminőség:** A `hotelguru-frontend` mappából futtathatók, vagy Docker-en keresztül:
    ```bash
    # Linting
    docker-compose exec frontend npm run lint
    # Formázás
    docker-compose exec frontend npm run format
    ```
* **Backend Tesztelés:**
    ```bash
    docker-compose exec app python -m pytest -v
    ```

## Konfiguráció Részletei

* **Docker Compose (`docker-compose.yml`):** Itt vannak definiálva a szolgáltatások (`app`, `frontend`, `db`), hálózatok, kötetek és a **konténerek környezeti változói**. Az itt megadott környezeti változók (pl. `VITE_API_BASE_URL`, `DB_USER`, `SECRET_KEY`) elsőbbséget élveznek.
* **Backend Konfiguráció (`config.py`):** Beolvassa a környezeti változókat, vagy alapértelmezett értékeket használ.
* **.env Fájlok:**
    * `Hotelguru_2/.env`: Elsősorban a **Docker nélküli** helyi futtatáshoz használatos a backend konfigurálására (adatbázis, titkos kulcsok). Docker Compose használatakor a `docker-compose.yml`-ben megadott értékek felülírják ezeket a konténer számára.
    * `hotelguru-frontend/.env`: Elsősorban a **Docker nélküli** helyi futtatáshoz használatos a frontend konfigurálására (`VITE_API_BASE_URL`). Docker Compose használatakor a `docker-compose.yml`-ben megadott `VITE_API_BASE_URL` ezt felülírja a böngészőnek szánt kód számára.
* **Biztonság:** **Éles környezetben a titkos kulcsokat és jelszavakat SOHA ne tárold a kódban, `.env` fájlokban vagy a `docker-compose.yml`-ben!** Használj biztonságosabb módszereket (pl. Docker secrets, környezeti változók a futtató platformon).

## Backend Kapcsolat és CORS

* A frontend Axios segítségével kommunikál a `VITE_API_BASE_URL`-en elérhető backenddel.
* A backend (`app` service) `Flask-Cors` kiterjesztéssel van konfigurálva (`app/__init__.py`), hogy engedélyezze a kéréseket a frontend origintől (`http://localhost:3000`). Ha CORS hibát tapasztalsz, ellenőrizd ezeket a beállításokat a backend kódban.

## Projekt Struktúra

* **`Hotelguru_2/`**: Backend API (Flask)
    * `app/`: Fő alkalmazás kód (blueprints, models, services stb.)
    * `migrations/`: Adatbázis migrációk
    * `tests/`: Backend tesztek
    * `run_app.py`, `config.py`, `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `init_db.py` stb.
* **`hotelguru-frontend/`**: Frontend (Vue.js)
    * `src/`: Fő alkalmazás kód (components, views, stores, router, services stb.)
    * `public/`: Statikus fájlok
    * `package.json`, `vite.config.js`, `Dockerfile`, `.env.example` stb.

*(Részletesebb struktúra leírásért lásd az eredeti backend/frontend README fájlokat.)*

## Leállítás (Docker)

A Docker konténerek leállításához és eltávolításához (a hálózatokkal együtt):

```bash
# A Hotelguru_2 mappából futtasd:
docker-compose down
Ez a parancs nem törli a mysql_data nevű Docker kötetet, így az adatbázis adatai megmaradnak a következő docker-compose up futtatásig. Ha teljesen tiszta adatbázissal akarsz indulni legközelebb, futtasd a docker volume rm hotelguru_2_mysql_data (vagy a pontos kötetnevet, amit a docker volume ls mutat) parancsot a docker-compose down után.

## Futtatás Docker Nélkül (Haladó / Alternatív)
Ez a módszer több kézi beállítást igényel és kevésbé ajánlott a környezeti különbségek miatt. Röviden:

Telepítsd a Node.js-t és a Pythont a gépedre.

Állíts be egy helyi MySQL adatbázist.

Klónozd a repót.

Hozd létre és töltsd ki a .env fájlokat a Hotelguru_2 és hotelguru-frontend mappákban a helyi MySQL és API beállításokkal (pl. a frontend .env-be VITE_API_BASE_URL=http://localhost:8888/api, a backend .env-be a helyi DB adatai).

Hoz létre Python virtuális környezetet a backendhez, telepítsd a requirements.txt-t (pip install -r requirements.txt).

Inicializáld a helyi backend adatbázist (flask db upgrade, python init_db.py).

Telepítsd a frontend függőségeket (cd hotelguru-frontend && npm install).

Indítsd el a backendet az egyik terminálban (flask run --port=8888).

Indítsd el a frontendet a másik terminálban (cd hotelguru-frontend && npm run dev).