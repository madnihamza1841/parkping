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
    return {
        'email': 'test@example.com',
        'password': 'StrongPass123!',
        'full_name': 'Test User',
    }


@pytest.fixture
def registered_user(db, user_data):
    return User.objects.create_user(**user_data)


@pytest.mark.django_db
def test_register(client, user_data):
    url = reverse('auth-register')
    resp = client.post(url, user_data, format='json')
    assert resp.status_code == 201
    assert 'password' not in resp.data
    assert 'phone_number' not in resp.data
    assert 'date_of_birth' not in resp.data


@pytest.mark.django_db
def test_register_duplicate_email(client, registered_user, user_data):
    url = reverse('auth-register')
    resp = client.post(url, user_data, format='json')
    assert resp.status_code == 400


@pytest.mark.django_db
def test_login(client, registered_user, user_data):
    url = reverse('auth-token')
    resp = client.post(url, {'email': user_data['email'], 'password': user_data['password']}, format='json')
    assert resp.status_code == 200
    assert 'access' in resp.data
    assert 'refresh' in resp.data


@pytest.mark.django_db
def test_token_refresh(client, registered_user, user_data):
    login = client.post(reverse('auth-token'), {'email': user_data['email'], 'password': user_data['password']}, format='json')
    refresh = login.data['refresh']
    resp = client.post(reverse('auth-token-refresh'), {'refresh': refresh}, format='json')
    assert resp.status_code == 200
    assert 'access' in resp.data


@pytest.mark.django_db
def test_profile_get(client, registered_user, user_data):
    login = client.post(reverse('auth-token'), {'email': user_data['email'], 'password': user_data['password']}, format='json')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + login.data['access'])
    resp = client.get(reverse('auth-profile'))
    assert resp.status_code == 200
    assert resp.data['email'] == user_data['email']
    assert 'phone_number' not in resp.data
    assert 'date_of_birth' not in resp.data


@pytest.mark.django_db
def test_profile_patch(client, registered_user, user_data):
    login = client.post(reverse('auth-token'), {'email': user_data['email'], 'password': user_data['password']}, format='json')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + login.data['access'])
    resp = client.patch(reverse('auth-profile'), {'full_name': 'Updated Name'}, format='json')
    assert resp.status_code == 200
    assert resp.data['full_name'] == 'Updated Name'
