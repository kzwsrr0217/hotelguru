# tests/test_user_api.py
import json

# A pytest automatikusan behúzza a fixture-öket a conftest.py-ból a nevük alapján

def test_user_login_success(client):
    """Teszteli a sikeres bejelentkezést (guest1)."""
    login_data = {
        'email': 'guest1@example.com', # Feltételezzük, hogy init_db.py futott
        'password': 'guest1pass'
    }
    response = client.post('/api/user/login', json=login_data)

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    response_data = response.get_json()
    assert 'access_token' in response_data
    assert 'refresh_token' in response_data

def test_user_login_admin_success(client):
    """Teszteli a sikeres bejelentkezést (admin)."""
    login_data = {
        'email': 'admin@hotel.test', # Feltételezzük, hogy init_db.py futott
        'password': 'adminpass'
    }
    response = client.post('/api/user/login', json=login_data)

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
    response_data = response.get_json()
    assert 'access_token' in response_data

def test_user_login_failure_wrong_password(client):
    """Teszteli a sikertelen bejelentkezést rossz jelszóval."""
    login_data = {
        'email': 'guest1@example.com',
        'password': 'wrongpassword'
    }
    response = client.post('/api/user/login', json=login_data)
    assert response.status_code == 401
    response_data = response.get_json()
    assert 'message' in response_data
    # Pontosabb ellenőrzés (kis/nagybetű érzéketlen lehet a válasz)
    assert 'incorrect e-mail or password' in response_data['message'].lower()

def test_user_login_failure_nonexistent_user(client):
    """Teszteli a sikertelen bejelentkezést nem létező felhasználóval."""
    login_data = {
        'email': 'nonexistent@example.com',
        'password': 'password'
    }
    response = client.post('/api/user/login', json=login_data)
    assert response.status_code == 401 # A service ugyanazt a hibát adja vissza
    response_data = response.get_json()
    assert 'message' in response_data
    assert 'incorrect e-mail or password' in response_data['message'].lower()