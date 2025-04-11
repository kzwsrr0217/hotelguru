# HotelGuru Frontend (Vue.js)

Ez a projekt a HotelGuru szállodamenedzsment rendszer felhasználói felületét (frontend) tartalmazza. Vue.js 3 keretrendszerre épül Vite build eszközzel, és a [HotelGuru Backend API](#backend) -val kommunikál.

## Technológiai Stack

* **Keretrendszer:** [Vue.js 3](https://vuejs.org/) (Composition API-val)
* **Build Eszköz:** [Vite](https://vitejs.dev/)
* **UI Könyvtár:** [Vuetify 3](https://vuetifyjs.com/en/) (Material Design)
* **Routing:** [Vue Router](https://router.vuejs.org/)
* **Állapotkezelés:** [Pinia](https://pinia.vuejs.org/)
* **API Hívások:** [Axios](https://axios-http.com/)
* **Nyelv:** JavaScript
* **Kódminőség:** ESLint, Prettier
* **Ikonok:** Material Design Icons (`@mdi/font`)

## Előfeltételek

1.  **Node.js:** Telepítve kell lennie a gépeden (LTS verzió ajánlott). Letöltés: [https://nodejs.org/](https://nodejs.org/) Ellenőrzés: `node -v` és `npm -v`. Az `npm` a Node.js része.
2.  **Futó Backend:** A HotelGuru backend API-nak futnia kell, és elérhetőnek kell lennie a frontend számára (alapértelmezetten a `http://localhost:8888/api` címen). Lásd a backend dokumentációját a beállításához (pl. `docker-compose up -d` a `Hotelguru_2` mappában).

## Telepítés és Beállítás

1.  **Repository Klónozása:** Ha még nem tetted meg, klónozd a teljes HotelGuru projektet (ami tartalmazza a backend és frontend mappákat is).
    ```bash
    # Példa:
    # git clone <repository_url>
    # cd <repository_root_folder>
    ```

2.  **Frontend Mappába Lépés:** Navigálj a frontend projekt mappájába:
    ```bash
    cd hotelguru-frontend
    ```

3.  **Függőségek Telepítése:** Telepítsd a szükséges npm csomagokat:
    ```bash
    npm install
    ```
    *(Ez letölti a `node_modules` mappa tartalmát a `package.json` alapján.)*

4.  **Konfiguráció (`.env` fájl):**
    * Hozz létre egy `.env` fájlt a `hotelguru-frontend` mappa gyökerében (a `package.json` mellett).
    * Másold bele a következő sort, hogy megadd a backend API elérési útját. Győződj meg róla, hogy az URL helyes (ahol a backend fut):
      ```dotenv
      # hotelguru-frontend/.env
      VITE_API_BASE_URL=http://localhost:8888/api
      ```

## Fejlesztői Szerver Futtatása

1.  Győződj meg róla, hogy a backend szerver fut (pl. Dockerben).
2.  A `hotelguru-frontend` mappában indítsd el a Vite fejlesztői szervert:
    ```bash
    npm run dev
    ```
3.  A terminál kiírja a címet, ahol a frontend elérhető (általában `http://localhost:5173`). Nyisd meg ezt a címet a böngésződben.
4.  A szerver figyeli a fájlok változását, és a legtöbb módosítás után automatikusan frissíti a böngészőt (Hot Module Replacement - HMR).

## Kódminőség Eszközök

* **Linting (Hibakeresés, Stílus):**
    ```bash
    npm run lint
    ```
* **Formázás (Kód egységesítése):**
    ```bash
    npm run format
    ```

## Projekt Struktúra (`src` mappa)

* `assets/`: Statikus fájlok (képek, globálisabb CSS, stb.).
* `components/`: Kisebb, újrafelhasználható UI komponensek.
* `layouts/` (Opcionális): Oldal elrendezési komponensek (pl. alapértelmezett, admin).
* `plugins/` (Opcionális): Vue pluginek konfigurációja (pl. Vuetify itt is lehetne).
* `router/`: `index.js` - Vue Router útvonalak és navigációs őrök definíciója.
* `services/`: API hívásokat kezelő modulok (pl. `apiClient.js`, `authService.js`, `roomService.js`).
* `stores/`: Pinia állapotkezelő modulok (pl. `auth.js`).
* `utils/` (Opcionális): Általános segédfüggvények (pl. formázók).
* `views/`: Oldal-szintű komponensek, amelyeket a router megjelenít (gyakran almappákba szervezve, pl. `views/admin/`).
* `App.vue`: A fő Vue komponens, ami tartalmazza az alap elrendezést (pl. `<v-app>`, `<v-app-bar>`, `<v-main>`) és a `<RouterView />`-t.
* `main.js`: Az alkalmazás belépési pontja, itt történik a Vue, Pinia, Router, Vuetify inicializálása és az alkalmazás csatlakoztatása a DOM-hoz (`#app`).

## Backend Kapcsolat

* A frontend az Axios segítségével kommunikál a `.env` fájlban megadott `VITE_API_BASE_URL` címen futó backend API-val.
* **CORS:** A backendnek megfelelően kell konfigurálva lennie a CORS (Cross-Origin Resource Sharing) kezelésére, hogy engedélyezze a frontend (`http://localhost:5173`) számára az API hívásokat. Lásd a backend `app/__init__.py` fájljában a `CORS(...)` beállításokat.
* **Authentikáció:** A bejelentkezés után kapott JWT (access token) automatikusan hozzáadódik az API kérések `Authorization: Bearer <token>` fejlécéhez az `src/services/apiClient.js`-ben definiált Axios interceptor segítségével.

## Fontosabb Backend Változások (Frontend Fejlesztés Során)

Az alábbi módosítások történtek a backend API-n a frontend fejlesztés támogatása érdekében:

1.  **CORS Engedélyezése:** A `Flask-Cors` kiterjesztés hozzáadva és konfigurálva az `app/__init__.py`-ban, hogy a frontendről érkező kéréseket engedélyezze.
2.  **`@bp.auth_required` Dekorátor Eltávolítása:** Több végpontról (`/reservations/mine`, `/reservation/cancel/...`, `/room/list_all_admin`, `/admin/rooms`, `/admin/rooms/...`) eltávolításra került ez a dekorátor, mert konfliktust okozott a `@jwt_required()`-dal és indokolatlan 401-es hibákat eredményezett. Az authentikációt/autorizációt a `@jwt_required()` és `@roles_required()` végzi, az `@bp.auth_required` elsősorban a Swagger UI integrációhoz kellene (ennek hiánya miatt a Swagger "Try it out" funkciója ezeknél a végpontoknál manuális `Authorization` fejléc beállítást igényelhet).
3.  **Új Végpont Szobák Szűrésére:** Létrehozva a `GET /api/room/rooms/available` végpont, ami `start_date` és `end_date` query paraméterek alapján szűr az elérhető szobákra (figyelembe véve a foglalásokat is).
4.  **Új Végpont Szoba Hozzáadására:** Létrehozva a `POST /api/admin/rooms` végpont új szobák hozzáadásához (Admin only).
5.  **Séma Javítások:**
    * `ReservationByUserSchema`: Az `id` mező hozzáadva (komment eltávolítva), hogy a frontend megkapja a foglalás azonosítóját.
    * `RoomAdminSchema`: A `room_type_id` mezőnél `allow_none=True` lett beállítva, hogy a `null` érték is elfogadott legyen szerkesztéskor.
6.  **Service Logika Javítások:**
    * `ReservationService.add_reservation`: Eltávolítva a hibás logika, ami a `Room.is_available`-t `False`-ra állította foglaláskor.
    * `ReservationService.cancel_reservation`: Javítva az `AttributeError: 'User' object has no attribute 'role'` hiba (a `user.roles` listát kell ellenőrizni).
    * `AdminService.update_room`: Javítva a logika, hogy helyesen kezelje, ha `room_type_id`-ként `None` érkezik (ne próbálja ellenőrizni az adatbázisban).
    * `AdminService.add_room`: Új függvény hozzáadva szoba létrehozásához, hibakezeléssel (pl. létező szobaszám).
    * `AdminService.delete_room`: Javítva a lekérdezés (`db.session.get`) és `rollback` hozzáadva hibaesetre.
7.  **Route Argumentum Javítások:** Az APIFlask `@bp.input` dekorátor által injektált argumentumok nevei javítva a route függvényekben (`query_data`, `json_data` használata `data` vagy `query_args` helyett).

## További Fejlesztés

* Implementáld a TODO elemeket a kódban (pl. Snackbar üzenetek, törlés és egyéb admin/recepciós funkciók véglegesítése).
* Bővítsd a UI-t további nézetekkel és komponensekkel a projektleírás alapján.
* Finomítsd a Vuetify témát és a stílusokat.
* Írj teszteket a frontend komponensekhez és logikához (pl. Vitest segítségével).