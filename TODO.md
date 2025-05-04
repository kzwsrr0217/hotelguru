


Funkcionális Követelmények

Vendég Funkciók:

Regisztráció/Login/Profil:

✅ Regisztráció (/user/registrate): Megvalósítva, létrehozza a felhasználót címmel, jelszót hashel, 'Guest' szerepkört rendel hozzá (UserService.user_registrate).

✅ Login (/user/login): Megvalósítva, ellenőrzi a jelszót, JWT access és refresh tokeneket ad vissza (UserService.user_login, app/__init__.py token generálás).

❗ Profil módosítás (/user/update/{uid}): frontenden még nincs kész

Szobák Megtekintése:

✅ Szobák listázása (bejelentkezés nélkül): Megvalósítva (/room/list, /room/rooms/available). A RoomService biztosítja a szűrést (dátummal/nélküle), csak az is_available=true szobákat listázza alapból.

Foglalás:

✅ Szobafoglalás (/reservation/add): Megvalósítva. A bejelentkezett felhasználó ID-ját a JWT tokenből nyeri ki (get_jwt_identity). A ReservationService.add_reservation kezeli a dátum validációt és az ütközésvizsgálatot (átfedő foglalások ellenőrzése _check_for_overlaps). A foglalás Depending státusszal jön létre.

✅ Foglalás lemondása (/reservation/cancel/{id}): Megvalósítva. A ReservationService.cancel_reservation ellenőrzi, hogy a felhasználó a sajátját mondja-e le (vagy admin/recepciós), a foglalás státusza (Depending, Success) megfelelő-e, és betartja-e a lemondási határidőt (MIN_CANCELLATION_DAYS). A státuszt Canceled-re állítja.

✅ Saját foglalások megtekintése (/reservation/reservations/mine): Megvalósítva. Lekérdezi a bejelentkezett felhasználó nem-lemondott foglalásait (ReservationService.serach_reservation_by_user).

Extra Szolgáltatások Rendelése:

❗ Hiányosság/Részleges Megvalósítás: A követelmény szerint a vendég rendelhet szolgáltatást tartózkodás alatt. A jelenlegi kódban ezt csak a recepciós teheti meg (/receptionist/reservations/{id}/services). Nincs dedikált vendég végpont/funkció erre. Frontenden nem elérhetőek a szolgáltatások

Recepciós Funkciók:

Foglalás Kezelés:

❗ Foglalások listázása (/receptionist/reservations): Megvalósítva (ReceptionistService.get_all_reservations). 
# Frontenden nincs kész

❗ Foglalás visszaigazolása (/reservation/reservations/{id}/confirm): Megvalósítva. A ReceptionistService.confirm_reservation (amit a reservation blueprint hív) ellenőrzi az ütközéseket és Depending -> Success státuszra vált.
# Frontenden nincs kész

Check-in / Check-out:

❗ Check-in (/receptionist/checkin/{id}): Megvalósítva. A ReceptionistService.check_in_guest ellenőrzi a státuszt (Success) és a dátumot, majd CheckedIn-re vált.*
# Frontenden nincs kész

✅ Check-out (/receptionist/checkout/{id}): Megvalósítva. A ReceptionistService.checkout_guest ellenőrzi a státuszt (CheckedIn) és a dátumot, CheckedOut-ra vált, véglegesíti a számlát (InvoiceService.get_or_create_invoice hívás calculate_final_amount=True-val és státusz Closed-ra állítása), és a szobát újra elérhetővé teszi.
# Frontenden nincs kész

Számlázás és Szolgáltatások:

✅ Szolgáltatások hozzáadása számlához (/receptionist/reservations/{id}/services): Megvalósítva. A ReceptionistService.add_services_to_reservation ellenőrzi a foglalás státuszát (CheckedIn), hozzáadja a szolgáltatásokat a számlához és frissíti az összeget.
# Frontenden nincs kész

✅ Számla kiállítása/letöltése (/invoice/download/{id}): Megvalósítva PDF generálással (WeasyPrint szükséges). Az InvoiceService lekéri és kiszámolja az adatokat.
# Frontenden nincs kész

Adminisztrátor Funkciók:

Szobakezelés (CRUD):

✅ Listázás (/admin/rooms GET): Megvalósítva (AdminService.get_all_rooms).

✅ Hozzáadás (/admin/rooms POST): Megvalósítva (AdminService.add_room). Ellenőrzi a szobaszám egyediségét, szobatípus létezését.

✅ Módosítás (/admin/rooms/{id} PUT): Megvalósítva (AdminService.update_room). Lehetővé teszi az adatok (ár, leírás, név, típus) és a foglalhatósági állapot (is_available) módosítását.

✅ Törlés (/admin/rooms/{id} DELETE): Megvalósítva (AdminService.delete_room).

Szolgáltatáskezelés (CRUD):

✅ Listázás, Lekérés ID alapján, Hozzáadás, Módosítás: Megvalósítva a /service blueprint alatt, Admin jogosultsághoz kötve.

⚠️ Törlés: A service_delete funkció ki van kommentelve a ServiceService-ben.

(Implicit) Jogosultságkezelés:

❗ Hiányosság: Nincsenek dedikált végpontok felhasználók szerepköreinek módosítására vagy felhasználók admin általi kezelésére (pl. törlés, aktiválás/deaktiválás).

Frontend Megfelelés (Magas Szinten):

✅ Az alapvető struktúra (Vue, Vite, Pinia, Vue Router, Vuetify) adott.

✅ A store (auth.js) kezeli a JWT tokent, a bejelentkezett állapotot és a szerepköröket (token dekódolásával).

✅ A router (router/index.js) tartalmaz navigációs gárdát (beforeEach), ami kezeli a védett útvonalakat (meta: { requiresAuth: true }) és a szerepkör alapú jogosultságot (meta: { roles: [...] }).

✅ Vannak dedikált service fájlok (pl. authService.js, roomService.js, reservationService.js, adminService.js), amelyek az apiClient-et használják a backend hívásokhoz. Az apiClient interceptorral rendelkezik a token automatikus hozzáadásához.

✅ A nézetek (views/) elkülönítve vannak, beleértve az admin nézetet is (views/admin/AdminRoomsView.vue).


Nem-Funkcionális Követelmények 

Teljesítmény & Skálázhatóság:

✅ Alapok: Docker Compose, JWT stateless, APIFlask/Flask és a Vue/Vite


Biztonság:

✅ Alapok: Jelszó hash (werkzeug.security). JWT authentikáció (Flask-JWT-Extended). Szerepkör alapú autorizáció (@roles_required, frontend router guard). CORS kezelés (Flask-Cors). Input validáció (Marshmallow sémák, APIFlask).

❗ Fejlesztési területek: HTTPS nincs beállítva (elengedhetetlen élesben!). JWT token tárolása localStorage-ban sebezhető XSS támadásokkal szemben (HttpOnly cookie biztonságosabb lehet). Titkos kulcsok (SECRET_KEY, JWT_SECRET_KEY) és DB jelszavak kezelése éles környezetben (ne a docker-compose.yml-ben legyenek plain textként). Részletesebb input validáció mindenhol. Védelem egyéb támadások ellen (pl. rate limiting). GDPR megfelelőség biztosítása.

Felhasználói Élmény:

✅ Alapok: Vue + Vuetify jó alapot ad egy modern, reszponzív és intuitív felülethez. A projekt struktúrája támogatja a karbantarthatóságot.


Megbízhatóság:

✅ Alapok: Docker konzisztens környezetet ad. Tranzakciókezelés (rollback hiba esetén) látható a service rétegben és a tesztekben (db_session fixture). restart: always a DB-nél.



Összegzés:


Hiányosságok/Fejlesztendő területek (Funkcionális):

Vendégek nem tudnak közvetlenül szolgáltatást rendelni.

Adminisztrátorok nem tudnak felhasználókat/szerepköröket kezelni.

Szolgáltatás törlés nincs implementálva/aktiválva.

A foglalás visszaigazolás végpontja logikusabban lehetne a /receptionist alatt.


