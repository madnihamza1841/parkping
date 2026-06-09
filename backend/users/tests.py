import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user_data():
    return {'email': 'test@example.com', 'password': 'StrongPass123!', 'full_name': 'Test User'}


@pytest.fixture
def registered_user(db, user_data):
    return User.objects.create_user(**user_data)


def _login(client, email, password='StrongPass123!'):
    resp = client.post(reverse('auth-token'), {'email': email, 'password': password}, format='json')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data['access'])
    return resp.data


# ── Registration ────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_register(client, user_data):
    resp = client.post(reverse('auth-register'), user_data, format='json')
    assert resp.status_code == 201
    assert 'password' not in resp.data
    assert 'phone_number' not in resp.data
    assert 'date_of_birth' not in resp.data


@pytest.mark.django_db
def test_register_duplicate_email(client, registered_user, user_data):
    resp = client.post(reverse('auth-register'), user_data, format='json')
    assert resp.status_code == 400
    assert 'detail' in resp.data


@pytest.mark.django_db
def test_register_missing_email(client):
    resp = client.post(reverse('auth-register'), {'password': 'Pass123!', 'full_name': 'X'}, format='json')
    assert resp.status_code == 400


@pytest.mark.django_db
def test_register_missing_password(client):
    resp = client.post(reverse('auth-register'), {'email': 'x@x.com', 'full_name': 'X'}, format='json')
    assert resp.status_code == 400


@pytest.mark.django_db
def test_register_weak_password(client):
    resp = client.post(reverse('auth-register'),
        {'email': 'new@x.com', 'password': '123', 'full_name': 'X'}, format='json')
    assert resp.status_code == 400


@pytest.mark.django_db
def test_register_with_optional_fields(client):
    resp = client.post(reverse('auth-register'), {
        'email': 'full@x.com', 'password': 'StrongPass123!',
        'full_name': 'Full User', 'date_of_birth': '1990-01-01', 'phone_number': '+447000000000',
    }, format='json')
    assert resp.status_code == 201
    # Optional PII fields still never returned
    assert 'date_of_birth' not in resp.data
    assert 'phone_number' not in resp.data


# ── Auth / JWT ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_login(client, registered_user, user_data):
    resp = client.post(reverse('auth-token'), {'email': user_data['email'], 'password': user_data['password']}, format='json')
    assert resp.status_code == 200
    assert 'access' in resp.data
    assert 'refresh' in resp.data


@pytest.mark.django_db
def test_login_wrong_password(client, registered_user):
    resp = client.post(reverse('auth-token'), {'email': 'test@example.com', 'password': 'wrong'}, format='json')
    assert resp.status_code == 401


@pytest.mark.django_db
def test_login_unknown_email(client, db):
    resp = client.post(reverse('auth-token'), {'email': 'nobody@x.com', 'password': 'Pass123!'}, format='json')
    assert resp.status_code == 401


@pytest.mark.django_db
def test_token_refresh(client, registered_user, user_data):
    tokens = client.post(reverse('auth-token'), {'email': user_data['email'], 'password': user_data['password']}, format='json').data
    resp = client.post(reverse('auth-token-refresh'), {'refresh': tokens['refresh']}, format='json')
    assert resp.status_code == 200
    assert 'access' in resp.data


@pytest.mark.django_db
def test_token_refresh_invalid(client, db):
    resp = client.post(reverse('auth-token-refresh'), {'refresh': 'not_a_real_token'}, format='json')
    assert resp.status_code == 401


@pytest.mark.django_db
def test_protected_endpoint_requires_auth(client, db):
    resp = client.get(reverse('auth-profile'))
    assert resp.status_code == 401


# ── Profile ──────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_profile_get(client, registered_user, user_data):
    _login(client, user_data['email'])
    resp = client.get(reverse('auth-profile'))
    assert resp.status_code == 200
    assert resp.data['email'] == user_data['email']
    assert 'phone_number' not in resp.data
    assert 'date_of_birth' not in resp.data


@pytest.mark.django_db
def test_profile_patch(client, registered_user, user_data):
    _login(client, user_data['email'])
    resp = client.patch(reverse('auth-profile'), {'full_name': 'Updated Name'}, format='json')
    assert resp.status_code == 200
    assert resp.data['full_name'] == 'Updated Name'


@pytest.mark.django_db
def test_profile_cannot_change_email(client, registered_user, user_data):
    _login(client, user_data['email'])
    resp = client.patch(reverse('auth-profile'), {'email': 'hacked@evil.com'}, format='json')
    # email is read-only on the serializer — original email unchanged
    assert resp.data['email'] == user_data['email']


@pytest.mark.django_db
def test_profile_another_user_cannot_access(client, registered_user, db):
    other = User.objects.create_user(email='other@x.com', password='StrongPass123!', full_name='Other')
    _login(client, 'other@x.com')
    resp = client.get(reverse('auth-profile'))
    # Returns OTHER user's own profile, not the first user's
    assert resp.data['email'] == 'other@x.com'
