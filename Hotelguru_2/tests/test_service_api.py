# tests/test_service_api.py
import json
from app.models.service import Service # Importáljuk a modellt a DB ellenőrzéshez
import time 

# A pytest automatikusan behúzza a fixture-öket (client, db_session, admin_auth_headers)

def test_add_service_success_admin(client, db_session, admin_auth_headers):
    """Teszteli új szolgáltatás hozzáadását adminisztrátorként."""
    # Egyedi név generálása (pl. időbélyeggel)
    unique_suffix = int(time.time() * 1000) # Milliszekundumok az egyediséghez
    service_name = f"Késői Kijelentkezés Teszt {unique_suffix}"
    # Vagy uuid használatával:
    # import uuid
    # service_name = f"Késői Kijelentkezés Teszt {uuid.uuid4()}"

    new_service_data = {
        "name": service_name, # <<< Egyedi név használata
        "description": "Lehetőség 14:00-ig maradni",
        "price": 5000.0
    }

    # Kérés küldése az admin authentikációs headerrel
    response = client.post('/api/service/add',
                           json=new_service_data,
                           headers=admin_auth_headers)

    # HTTP válasz ellenőrzése
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}. Response: {response.text}"
    response_data = response.get_json()
    assert response_data['name'] == new_service_data['name'] # Ellenőrizzük az egyedi nevet
    assert response_data['price'] == new_service_data['price']

    # Adatbázis állapotának ellenőrzése (a rollback előtt!)
    created_service = db_session.query(Service).filter_by(name=new_service_data['name']).one_or_none()
    assert created_service is not None, "Service was not found in DB after API call (before rollback)"
    assert created_service.description == new_service_data['description']
    assert created_service.price == new_service_data['price']

    # A teszt végén a db_session fixture automatikusan visszavonja a tranzakciót,
    # így ez a "Késői Kijelentkezés Teszt" szolgáltatás nem marad az adatbázisban.

def test_add_service_fail_unauthorized(client):
    """Teszteli, hogy authentikáció nélkül nem lehet szolgáltatást hozzáadni."""
    new_service_data = {
        "name": "Jogosulatlan Szolgáltatás",
        "description": "Ezt nem lenne szabad hozzáadni",
        "price": 1000.0
    }
    response = client.post('/api/service/add', json=new_service_data) # Nincsenek headerek
    assert response.status_code == 401 # Várhatóan Unauthorized

def test_add_service_fail_guest_role(client, db_session, guest_auth_headers):
    """Teszteli, hogy 'Guest' szerepkörrel nem lehet szolgáltatást hozzáadni."""
    new_service_data = {
        "name": "Vendég Által Hozzáadott Szolgáltatás",
        "description": "Ezt sem lenne szabad hozzáadni",
        "price": 2000.0
    }
    response = client.post('/api/service/add',
                           json=new_service_data,
                           headers=guest_auth_headers) # Vendég tokenjével

    assert response.status_code == 403, f"Expected status code 403, got {response.status_code}. Response: {response.text}"

    # Ellenőrizzük, hogy tényleg nem került be a DB-be
    service_in_db = db_session.query(Service).filter_by(name=new_service_data['name']).one_or_none()
    assert service_in_db is None, "Service was created with Guest role, but shouldn't have been."