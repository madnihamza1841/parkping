"""
Integration tests: full end-to-end flows across all apps.
"""
import uuid
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from cars.models import Car
from chat.models import ChatThread, Message
from calls.models import CallLog
from notifications.models import DeviceToken

User = get_user_model()


@pytest.mark.django_db
def test_full_scan_chat_call_flow(visitor_client, owner_client, car, owner):
    anon = APIClient()
    car_uuid = str(car.uuid)

    # 1. Scan — public, no auth
    scan = anon.get(reverse('car-scan', kwargs={'car_uuid': car_uuid}))
    assert scan.status_code == 200
    assert set(scan.data.keys()) == {'uuid', 'nickname', 'make', 'model'}

    # 2. Visitor starts chat
    start = visitor_client.post(reverse('chat-start', kwargs={'car_uuid': car_uuid}))
    assert start.status_code == 201
    thread_id = start.data['uuid']

    # 3. Visitor sends message — label Visitor, no sender PII
    msg = visitor_client.post(
        reverse('chat-messages', kwargs={'thread_id': thread_id}),
        {'content': 'Please move your car!'}, format='json')
    assert msg.status_code == 201
    assert msg.data['sender_label'] == 'Visitor'
    assert 'sender' not in msg.data

    # 4. Owner replies — label Car Owner
    reply = owner_client.post(
        reverse('chat-messages', kwargs={'thread_id': thread_id}),
        {'content': 'On my way!'}, format='json')
    assert reply.status_code == 201
    assert reply.data['sender_label'] == 'Car Owner'

    # 5. Visitor requests call token
    call = visitor_client.post(reverse('call-token', kwargs={'car_uuid': car_uuid}))
    assert call.status_code == 201
    channel_id = call.data['channel_id']

    # 6. Owner declines
    decline = visitor_client.post(
        reverse('call-status', kwargs={'channel_id': channel_id}),
        {'status': 'declined'}, format='json')
    assert decline.status_code == 200

    # 7. System message appears in thread
    msgs = visitor_client.get(reverse('chat-messages', kwargs={'thread_id': thread_id}))
    system = [m for m in msgs.data if m.get('is_system')]
    assert len(system) >= 1
    assert 'declined' in system[0]['content']


@pytest.mark.django_db
def test_pii_never_leaked_in_any_response(visitor_client, owner_client, car, owner):
    car_uuid = str(car.uuid)
    start = visitor_client.post(reverse('chat-start', kwargs={'car_uuid': car_uuid}))
    thread_id = start.data['uuid']
    visitor_client.post(reverse('chat-messages', kwargs={'thread_id': thread_id}), {'content': 'Hi'}, format='json')
    owner_client.post(reverse('chat-messages', kwargs={'thread_id': thread_id}), {'content': 'Yes'}, format='json')

    for resp in [
        visitor_client.get(reverse('car-scan', kwargs={'car_uuid': car_uuid})),
        visitor_client.get(reverse('chat-threads')),
        visitor_client.get(reverse('chat-messages', kwargs={'thread_id': thread_id})),
    ]:
        body = str(resp.data)
        assert owner.email not in body


@pytest.mark.django_db
def test_multiple_visitors_isolated_threads(make_user, db):
    owner = make_user('owner@multi.test')
    car1 = Car.objects.create(owner=owner, plate_number='M001', make='A', model='B', colour='C', nickname='Car1')
    car2 = Car.objects.create(owner=owner, plate_number='M002', make='D', model='E', colour='F', nickname='Car2')

    def mk(email):
        c = APIClient()
        r = c.post(reverse('auth-token'), {'email': email, 'password': 'Pass1234!'}, format='json')
        c.credentials(HTTP_AUTHORIZATION='Bearer ' + r.data['access'])
        return c

    make_user('v1@multi.test')
    make_user('v2@multi.test')
    c1, c2 = mk('v1@multi.test'), mk('v2@multi.test')

    t1 = c1.post(reverse('chat-start', kwargs={'car_uuid': str(car1.uuid)})).data['uuid']
    t2 = c2.post(reverse('chat-start', kwargs={'car_uuid': str(car2.uuid)})).data['uuid']
    assert t1 != t2
    assert ChatThread.objects.count() == 2

    # v1 cannot see v2's thread
    ids = [t['uuid'] for t in c1.get(reverse('chat-threads')).data]
    assert t1 in ids
    assert t2 not in ids


@pytest.mark.django_db
def test_two_calls_create_two_logs(visitor_client, car):
    r1 = visitor_client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    r2 = visitor_client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    assert r1.data['channel_id'] != r2.data['channel_id']
    assert CallLog.objects.count() == 2


@pytest.mark.django_db
def test_device_tokens_all_platforms(visitor_client):
    for platform, token in [('android', 'tok_a'), ('ios', 'tok_i'), ('web', 'tok_w')]:
        resp = visitor_client.post(reverse('notifications-register-device'),
                                   {'token': token, 'platform': platform}, format='json')
        assert resp.status_code == 200
    assert DeviceToken.objects.count() == 3


@pytest.mark.django_db
def test_all_error_responses_have_detail_key(db):
    anon = APIClient()
    cases = [
        ('post', reverse('auth-register'), {'email': 'bad'}),
        ('post', reverse('auth-token'), {'email': 'x@x.com', 'password': 'wrong'}),
        ('post', reverse('notifications-register-device'), {'token': 'x', 'platform': 'fax'}),
    ]
    for method, url, data in cases:
        resp = getattr(anon, method)(url, data, format='json')
        assert resp.status_code >= 400
        assert 'detail' in resp.data, f'No detail in {url}: {resp.data}'


@pytest.mark.django_db
def test_protected_endpoints_require_auth(db):
    anon = APIClient()
    fake_uuid = str(uuid.uuid4())
    for method, url in [
        ('get',  reverse('auth-profile')),
        ('get',  reverse('car-list')),
        ('post', reverse('chat-start', kwargs={'car_uuid': fake_uuid})),
        ('get',  reverse('chat-threads')),
        ('post', reverse('call-token', kwargs={'car_uuid': fake_uuid})),
        ('post', reverse('notifications-register-device')),
    ]:
        resp = getattr(anon, method)(url, format='json')
        assert resp.status_code == 401, f'{method.upper()} {url} returned {resp.status_code}'


@pytest.mark.django_db
def test_car_ownership_isolation(make_user, db):
    u1 = make_user('u1@iso.test')
    make_user('u2@iso.test')
    car = Car.objects.create(owner=u1, plate_number='ISO001', make='X', model='Y', colour='Z', nickname='U1 Car')

    c2 = APIClient()
    r = c2.post(reverse('auth-token'), {'email': 'u2@iso.test', 'password': 'Pass1234!'}, format='json')
    c2.credentials(HTTP_AUTHORIZATION='Bearer ' + r.data['access'])

    for url in [
        reverse('car-detail', kwargs={'uuid': str(car.uuid)}),
        reverse('car-qr', kwargs={'uuid': str(car.uuid)}),
        reverse('car-qr-pdf', kwargs={'uuid': str(car.uuid)}),
    ]:
        assert c2.get(url).status_code == 404, f'Expected 404 at {url}'
