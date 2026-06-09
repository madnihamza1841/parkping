import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from cars.models import Car
from calls.models import CallLog
from chat.models import Message, ChatThread

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
    return Car.objects.create(owner=owner, plate_number='CAL001', make='BMW',
                              model='3 Series', colour='Blue', nickname='Blue BMW')


def auth(client, email):
    resp = client.post(reverse('auth-token'), {'email': email, 'password': 'Pass1234!'}, format='json')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data['access'])


# ── Token generation ──────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_call_token_structure(client, visitor, car):
    auth(client, 'visitor@example.com')
    resp = client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    assert resp.status_code == 201
    assert 'channel_id' in resp.data
    assert 'token' in resp.data
    assert 'app_id' in resp.data


@pytest.mark.django_db
def test_call_token_channel_id_length(client, visitor, car):
    auth(client, 'visitor@example.com')
    resp = client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    assert len(resp.data['channel_id']) == 20


@pytest.mark.django_db
def test_each_call_gets_unique_channel_id(client, visitor, car):
    auth(client, 'visitor@example.com')
    r1 = client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    r2 = client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    assert r1.data['channel_id'] != r2.data['channel_id']


@pytest.mark.django_db
def test_call_token_requires_auth(client, db, car):
    resp = client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    assert resp.status_code == 401


@pytest.mark.django_db
def test_call_token_unknown_car(client, visitor, db):
    import uuid
    auth(client, 'visitor@example.com')
    resp = client.post(reverse('call-token', kwargs={'car_uuid': str(uuid.uuid4())}))
    assert resp.status_code == 404


# ── Call log ──────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_call_log_created(client, visitor, car):
    auth(client, 'visitor@example.com')
    client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    assert CallLog.objects.count() == 1
    log = CallLog.objects.first()
    assert log.status == 'initiated'
    assert log.initiated_by == visitor
    assert log.car == car


@pytest.mark.django_db
def test_call_log_thread_linked(client, visitor, car):
    auth(client, 'visitor@example.com')
    client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    log = CallLog.objects.first()
    assert log.thread is not None
    assert log.thread.scanner == visitor


# ── Call status transitions ───────────────────────────────────────────────────

@pytest.mark.django_db
def test_call_answered(client, visitor, car):
    auth(client, 'visitor@example.com')
    resp = client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    status_resp = client.post(reverse('call-status', kwargs={'channel_id': resp.data['channel_id']}),
                               {'status': 'answered'}, format='json')
    assert status_resp.status_code == 200
    assert CallLog.objects.first().status == 'answered'


@pytest.mark.django_db
def test_call_ended_with_duration(client, visitor, car):
    auth(client, 'visitor@example.com')
    resp = client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    client.post(reverse('call-status', kwargs={'channel_id': resp.data['channel_id']}),
                {'status': 'ended', 'duration_seconds': 120}, format='json')
    log = CallLog.objects.first()
    assert log.status == 'ended'
    assert log.duration_seconds == 120


@pytest.mark.django_db
def test_call_declined_inserts_system_message(client, visitor, car):
    auth(client, 'visitor@example.com')
    resp = client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    client.post(reverse('call-status', kwargs={'channel_id': resp.data['channel_id']}),
                {'status': 'declined'}, format='json')
    assert Message.objects.filter(is_system=True, content__icontains='declined').exists()


@pytest.mark.django_db
def test_call_missed_inserts_system_message(client, visitor, car):
    auth(client, 'visitor@example.com')
    resp = client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    client.post(reverse('call-status', kwargs={'channel_id': resp.data['channel_id']}),
                {'status': 'missed'}, format='json')
    assert Message.objects.filter(is_system=True, content__icontains='missed').exists()


@pytest.mark.django_db
def test_call_answered_no_system_message(client, visitor, car):
    auth(client, 'visitor@example.com')
    resp = client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    client.post(reverse('call-status', kwargs={'channel_id': resp.data['channel_id']}),
                {'status': 'answered'}, format='json')
    assert Message.objects.filter(is_system=True).count() == 0


@pytest.mark.django_db
def test_call_status_invalid_value(client, visitor, car):
    auth(client, 'visitor@example.com')
    resp = client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    bad = client.post(reverse('call-status', kwargs={'channel_id': resp.data['channel_id']}),
                      {'status': 'flying'}, format='json')
    assert bad.status_code == 400
    assert 'detail' in bad.data


@pytest.mark.django_db
def test_call_status_unknown_channel(client, visitor, db):
    auth(client, 'visitor@example.com')
    resp = client.post(reverse('call-status', kwargs={'channel_id': 'nonexistentchannel00'}),
                       {'status': 'ended'}, format='json')
    assert resp.status_code == 404


@pytest.mark.django_db
def test_system_message_not_attributed_to_any_user(client, visitor, car):
    auth(client, 'visitor@example.com')
    resp = client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    client.post(reverse('call-status', kwargs={'channel_id': resp.data['channel_id']}),
                {'status': 'declined'}, format='json')
    sys_msg = Message.objects.filter(is_system=True).first()
    assert sys_msg.sender is None
