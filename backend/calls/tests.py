import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from cars.models import Car
from calls.models import CallLog
from chat.models import Message

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def owner(db):
    return User.objects.create_user(email='owner@example.com', password='Pass1234!', full_name='Owner')


@pytest.fixture
def visitor(db):
    return User.objects.create_user(email='visitor@example.com', password='Pass1234!', full_name='Visitor')


@pytest.fixture
def car(owner):
    return Car.objects.create(owner=owner, plate_number='CAL001', make='BMW', model='3 Series', colour='Blue', nickname='Blue BMW')


def auth(client, email):
    resp = client.post(reverse('auth-token'), {'email': email, 'password': 'Pass1234!'}, format='json')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data['access'])


@pytest.mark.django_db
def test_call_token_structure(client, visitor, car):
    auth(client, 'visitor@example.com')
    resp = client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    assert resp.status_code == 201
    assert 'channel_id' in resp.data
    assert 'token' in resp.data
    assert 'app_id' in resp.data
    assert len(resp.data['channel_id']) == 20


@pytest.mark.django_db
def test_call_log_created(client, visitor, car):
    auth(client, 'visitor@example.com')
    client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    assert CallLog.objects.count() == 1
    log = CallLog.objects.first()
    assert log.status == 'initiated'
    assert log.initiated_by == visitor


@pytest.mark.django_db
def test_call_declined_inserts_system_message(client, visitor, car):
    auth(client, 'visitor@example.com')
    resp = client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    channel_id = resp.data['channel_id']
    status_resp = client.post(reverse('call-status', kwargs={'channel_id': channel_id}), {'status': 'declined'}, format='json')
    assert status_resp.status_code == 200
    assert Message.objects.filter(is_system=True, content__icontains='declined').exists()


@pytest.mark.django_db
def test_call_status_invalid(client, visitor, car):
    auth(client, 'visitor@example.com')
    resp = client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    channel_id = resp.data['channel_id']
    bad = client.post(reverse('call-status', kwargs={'channel_id': channel_id}), {'status': 'flying'}, format='json')
    assert bad.status_code == 400
