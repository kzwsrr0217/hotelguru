import functools  # Szükséges a @wraps-hoz

# JWT funkciók importálása
from flask_jwt_extended import verify_jwt_in_request, get_jwt

# APIFlask hiba importálása
from apiflask import HTTPError


def roles_required(*required_roles):
    """
    Egyedi dekorátor, amely ellenőrzi, hogy a felhasználó rendelkezik-e
    a megadott szerepkörök legalább egyikével.

    A szerepköröket a JWT token 'roles' claim-jéből olvassa ki.
    A dekorátort a @jwt_required() UTÁN kell használni.

    Args:
        *required_roles: Egy vagy több elfogadott szerepkör neve stringként.
                         Pl. @roles_required('Admin', 'Receptionist')
    """

    def decorator(func):
        @functools.wraps(func)  # Megőrzi az eredeti függvény metaadatait
        def wrapper(*args, **kwargs):
            # 1. Ellenőrzi, hogy érvényes JWT token van-e a kérésben
            #    (Ez hibát dob, ha nincs, amit a flask-jwt-extended kezel)
            verify_jwt_in_request()

            # 2. Lekérdezi a teljes JWT payloadot (claims)
            jwt_payload = get_jwt()

            # 3. Kiolvassa a felhasználó szerepköreit a tokenből
            #    (Üres listát ad vissza, ha nincs 'roles' claim)
            user_roles = jwt_payload.get("roles", [])

            # 4. Ellenőrzi, hogy van-e átfedés a felhasználó és az elvárt szerepkörök között
            #    Halmazműveletet használunk az egyszerű ellenőrzéshez
            allowed_roles_set = set(required_roles)
            user_roles_set = set(user_roles)

            if not allowed_roles_set.intersection(user_roles_set):
                # Ha nincs közös elem (a felhasználónak nincs meg egyik szükséges szerepköre sem)
                raise HTTPError(
                    403, message="Hozzáférés megtagadva: Nincs megfelelő jogosultsága."
                )  # 403 Forbidden

            # 5. Ha a jogosultság rendben van, meghívja az eredeti végpont függvényt
            return func(*args, **kwargs)

        return wrapper

    return decorator


"""
roles_required(*required_roles): A dekorátorunk egy külső függvény, ami argumentumként fogadja a szükséges szerepkörök neveit (*required_roles miatt tetszőleges számút megadhatsz, pl. 'Admin', 'Receptionist').
decorator(func): Ez a belső függvény kapja meg magát a dekorálandó végpont függvényt (func).
@functools.wraps(func): Ez egy standard Python segédfüggvény, ami biztosítja, hogy a dekorált függvény (pl. guest_check_in) megtartsa az eredeti nevét, dokumentációját stb., ami hasznos a debuggolásnál és a dokumentáció generálásánál.
wrapper(*args, **kwargs): Ez az a függvény, ami ténylegesen lefut a végpont függvény helyett.
verify_jwt_in_request(): Először ellenőrzi, hogy van-e érvényes JWT a kérésben. Ha nincs, ez a függvény (illetve a flask-jwt-extended) hibát dob (általában 401 Unauthorized), és a wrapper többi része nem fut le.
get_jwt(): Lekéri a dekódolt JWT token tartalmát (payload/claims).
jwt_payload.get('roles', []): Kivesszük a tokenből a roles listát, amit az előző lépésben adtunk hozzá. Ha valamiért hiányozna, egy üres listát kapunk vissza.
set(required_roles).intersection(set(user_roles)): Halmaz metszetet képezünk az elvárt és a felhasználó által birtokolt szerepkörök között. Ha a metszet nem üres (vagyis van legalább egy közös szerepkör), akkor a felhasználó jogosult.
if not ... intersection ...: Ha a metszet üres (nincs jogosultság), akkor egy HTTPError-t dobunk 403 Forbidden státuszkóddal és egy hibaüzenettel. Az apiflask ezt automatikusan kezeli és visszaadja a kliensnek.
return func(*args, **kwargs): Ha a felhasználónak van megfelelő jogosultsága, akkor meghívjuk az eredeti végpont függvényt (pl. guest_check_in) a kapott argumentumokkal, és visszaadjuk annak eredményét.
"""
