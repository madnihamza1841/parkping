import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from notifications.models import DeviceToken

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(email='user@example.com', password='Pass1234!', full_name='Test')


def auth(client, email='user@example.com'):
    resp = client.post(reverse('auth-token'), {'email': email, 'password': 'Pass1234!'}, format='json')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data['access'])


@pytest.mark.django_db
def test_register_device(client, user):
    auth(client)
    resp = client.post(reverse('notifications-register-device'), {'token': 'fcm_token_abc', 'platform': 'android'}, format='json')
    assert resp.status_code == 200
    assert DeviceToken.objects.count() == 1


@pytest.mark.django_db
def test_register_device_upsert(client, user):
    auth(client)
    client.post(reverse('notifications-register-device'), {'token': 'same_token', 'platform': 'android'}, format='json')
    client.post(reverse('notifications-register-device'), {'token': 'same_token', 'platform': 'android'}, format='json')
    assert DeviceToken.objects.count() == 1


@pytest.mark.django_db
def test_register_device_invalid_platform(client, user):
    auth(client)
    resp = client.post(reverse('notifications-register-device'), {'token': 'tok', 'platform': 'fax'}, format='json')
    assert resp.status_code == 400


@pytest.mark.django_db
def test_register_web_token(client, user):
    auth(client)
    resp = client.post(reverse('notifications-register-device'), {'token': 'web_push_token', 'platform': 'web'}, format='json')
    assert resp.status_code == 200
    assert DeviceToken.objects.filter(platform='web').count() == 1
