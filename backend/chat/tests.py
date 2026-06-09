import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from cars.models import Car
from chat.models import ChatThread, Message

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
def third_party(db):
    return User.objects.create_user(email='stranger@example.com', password='Pass1234!', full_name='Stranger')


@pytest.fixture
def car(owner):
    return Car.objects.create(owner=owner, plate_number='CAR001', make='Toyota',
                              model='Camry', colour='Black', nickname='Black Camry')


def auth(client, email, password='Pass1234!'):
    resp = client.post(reverse('auth-token'), {'email': email, 'password': password}, format='json')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data['access'])
    return client


# ── Thread creation ───────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_start_chat_creates_thread(client, visitor, car):
    auth(client, 'visitor@example.com')
    resp = client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))
    assert resp.status_code == 201
    assert ChatThread.objects.count() == 1


@pytest.mark.django_db
def test_start_chat_idempotent(client, visitor, car):
    auth(client, 'visitor@example.com')
    client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))
    resp = client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))
    assert resp.status_code == 200
    assert ChatThread.objects.count() == 1


@pytest.mark.django_db
def test_owner_cannot_chat_with_own_car(client, owner, car):
    auth(client, 'owner@example.com')
    resp = client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))
    assert resp.status_code == 400


@pytest.mark.django_db
def test_start_chat_requires_auth(client, db, car):
    resp = client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))
    assert resp.status_code == 401


@pytest.mark.django_db
def test_start_chat_unknown_car(client, visitor, db):
    import uuid as _uuid
    auth(client, 'visitor@example.com')
    resp = client.post(reverse('chat-start', kwargs={'car_uuid': str(_uuid.uuid4())}))
    assert resp.status_code == 404


# ── Messaging ─────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_send_message_visitor_label(client, visitor, car):
    auth(client, 'visitor@example.com')
    client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))
    thread = ChatThread.objects.first()
    resp = client.post(reverse('chat-messages', kwargs={'thread_id': str(thread.uuid)}),
                       {'content': 'Hello!'}, format='json')
    assert resp.status_code == 201
    assert resp.data['sender_label'] == 'Visitor'
    assert 'sender' not in resp.data


@pytest.mark.django_db
def test_send_message_owner_label(client, owner, visitor, car):
    visitor_client = APIClient()
    auth(visitor_client, 'visitor@example.com')
    visitor_client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))
    thread = ChatThread.objects.first()

    auth(client, 'owner@example.com')
    resp = client.post(reverse('chat-messages', kwargs={'thread_id': str(thread.uuid)}),
                       {'content': 'Coming!'}, format='json')
    assert resp.data['sender_label'] == 'Car Owner'


@pytest.mark.django_db
def test_third_party_cannot_send_message(client, third_party, visitor, car):
    visitor_client = APIClient()
    auth(visitor_client, 'visitor@example.com')
    visitor_client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))
    thread = ChatThread.objects.first()

    auth(client, 'stranger@example.com')
    resp = client.post(reverse('chat-messages', kwargs={'thread_id': str(thread.uuid)}),
                       {'content': 'Intrusion!'}, format='json')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_third_party_cannot_read_messages(client, third_party, visitor, car):
    visitor_client = APIClient()
    auth(visitor_client, 'visitor@example.com')
    visitor_client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))
    thread = ChatThread.objects.first()

    auth(client, 'stranger@example.com')
    resp = client.get(reverse('chat-messages', kwargs={'thread_id': str(thread.uuid)}))
    assert resp.status_code == 403


@pytest.mark.django_db
def test_message_content_is_not_empty(client, visitor, car):
    auth(client, 'visitor@example.com')
    client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))
    thread = ChatThread.objects.first()
    resp = client.post(reverse('chat-messages', kwargs={'thread_id': str(thread.uuid)}),
                       {'content': ''}, format='json')
    assert resp.status_code == 400


# ── Anonymisation ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_message_list_never_exposes_sender_id_or_email(client, visitor, car):
    auth(client, 'visitor@example.com')
    client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))
    thread = ChatThread.objects.first()
    client.post(reverse('chat-messages', kwargs={'thread_id': str(thread.uuid)}),
                {'content': 'Hi'}, format='json')
    resp = client.get(reverse('chat-messages', kwargs={'thread_id': str(thread.uuid)}))
    body = str(resp.data)
    assert 'visitor@example.com' not in body
    assert 'owner@example.com' not in body
    for msg in resp.data:
        assert 'sender' not in msg
        assert 'sender_id' not in msg


@pytest.mark.django_db
def test_thread_list_never_exposes_participant_details(client, visitor, owner, car):
    auth(client, 'visitor@example.com')
    client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))

    owner_client = APIClient()
    auth(owner_client, 'owner@example.com')
    resp = owner_client.get(reverse('chat-threads'))
    body = str(resp.data)
    assert 'visitor@example.com' not in body
    assert 'Pass1234' not in body


# ── Thread visibility ─────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_thread_visible_to_owner(client, owner, visitor, car):
    visitor_client = APIClient()
    auth(visitor_client, 'visitor@example.com')
    visitor_client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))

    auth(client, 'owner@example.com')
    resp = client.get(reverse('chat-threads'))
    assert resp.status_code == 200
    assert len(resp.data) == 1


@pytest.mark.django_db
def test_thread_not_visible_to_third_party(client, third_party, visitor, car):
    visitor_client = APIClient()
    auth(visitor_client, 'visitor@example.com')
    visitor_client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))

    auth(client, 'stranger@example.com')
    resp = client.get(reverse('chat-threads'))
    assert resp.status_code == 200
    assert len(resp.data) == 0  # stranger sees nothing


@pytest.mark.django_db
def test_system_message_label(visitor, car):
    thread = ChatThread.objects.create(scanner=visitor, car=car)
    msg = Message.objects.create(thread=thread, sender=None, content='Call declined.', is_system=True)
    assert msg.is_system is True
    assert msg.sender is None
