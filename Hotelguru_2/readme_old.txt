# HotelGuru API

Ez a projekt a HotelGuru szállodamenedzsment rendszer backend API-ját tartalmazza Flask, APIFlask és SQLAlchemy használatával, Docker Compose segítségével futtatható környezetben, MySQL adatbázissal.

## Előfeltételek

* **Docker:** Telepítve és futtatva ([https://www.docker.com/get-started](https://www.docker.com/get-started)). Docker Compose általában a Docker Desktop (Windows/macOS) vagy a Docker Engine (Linux) része.
* **Git:** A kód letöltéséhez.
* **(Opcionális) MySQL Kliens:** Adatbázis-kezelő eszköz (pl. MySQL Workbench, DBeaver, HeidiSQL) az adatbázis tartalmának közvetlen ellenőrzéséhez.

## Telepítés és Indítás Docker Compose segítségével

1.  **Tároló Klónozása:**
    ```bash
    git clone <repository_url>
    cd <repository_folder_name> 
    ```
    *(Cseréld le a `<repository_url>`-t és `<repository_folder_name>`-t a valós adatokra)*

2.  **Konténerek Építése és Indítása:**
    Ez a parancs megépíti a Docker image-eket (ha még nem léteznek vagy változtak), létrehozza a szükséges hálózatot és köteteket, majd elindítja a Flask alkalmazást (`app`) és a MySQL adatbázist (`db`) tartalmazó konténereket a háttérben (`-d` kapcsoló).
    ```bash
    docker-compose up --build -d
    ```
    Várj egy kicsit, amíg a MySQL adatbázis elindul és "egészséges" állapotba kerül (ezt az `app` konténer megvárja a `depends_on` és `healthcheck` beállítások miatt). A folyamatot a `docker-compose logs -f` paranccsal követheted.

3.  **Adatbázis Inicializálása (Csak az első indításkor, vagy ha törölted a kötetet):**
    Mivel az adatbázis most már a Docker köteten belül jön létre és él, az első indítás után inicializálni kell a sémát és feltölteni az adatokat az `app` konténeren belül:
    * **Migráció Létrehozása (ha még nincs):** Ha ez az első alkalom, vagy ha változtattál a modelleken:
        ```bash
        docker-compose exec app flask db migrate -m "Initial migration for MySQL" 
        ```
        *(A `-m "..."` üzenet lehet más is, ha már létezik history)*
    * **Migráció Alkalmazása (Séma Létrehozása/Frissítése):**
        ```bash
        docker-compose exec app flask db upgrade
        ```
    * **Adatok Feltöltése (Seed):**
        ```bash
        docker-compose exec app python init_db.py
        ```

4.  **Alkalmazás Elérése:**
    * Az API most már elérhető a `http://localhost:8888` címen.
    * A Swagger UI dokumentáció itt található: `http://localhost:8888/swagger`

5.  **Adatbázis Elérése (Opcionális):**
    * Használj egy MySQL klienst a csatlakozáshoz a következő adatokkal:
        * **Host:** `localhost`
        * **Port:** `3307` (Ezt állítottuk be a `docker-compose.yml`-ben!)
        * **Felhasználó:** `hotel_user`
        * **Jelszó:** `hotel_password`
        * **Adatbázis/Séma:** `hotel_db`

## Leállítás

A konténerek leállításához és eltávolításához (a hálózatot is beleértve) futtasd:
```bash
docker-compose down

Ez a parancs nem törli a mysql_data nevű Docker kötetet,
 így az adatbázis adatai megmaradnak a következő docker-compose up indításig.
  Ha teljesen tiszta adatbázissal akarsz indulni legközelebb, futtasd a docker volume rm <VOLUME_NAME> parancsot
   (a kötet nevét a docker volume ls paranccsal vagy a docker-compose up kimenetéből tudod meg, valószínűleg projektneve_mysql_data lesz)
   a docker-compose down után.

Konfiguráció
Az alkalmazás alapértelmezett konfigurációja a config.py-ban található. 
A docker-compose.yml-ben környezeti változókkal (environment szekció) lehetőség van felülbírálni az adatbázis kapcsolati adatokat
 és a FLASK_DEBUG módot. A titkos kulcsok (SECRET_KEY, JWT_SECRET_KEY) szintén környezeti változókból olvashatók be (config.py),
  és éles környezetben ezeket a Docker Compose fájlon kívülről kellene megadni.

docker leállítás és újra indítás a változtatások miatt:
docker-compose down
docker-compose up --build -d