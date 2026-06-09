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
def car(owner):
    return Car.objects.create(owner=owner, plate_number='CAR001', make='Toyota', model='Camry', colour='Black', nickname='Black Camry')


def auth(client, email, password='Pass1234!'):
    resp = client.post(reverse('auth-token'), {'email': email, 'password': password}, format='json')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data['access'])
    return client


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
def test_send_message(client, visitor, car):
    auth(client, 'visitor@example.com')
    client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))
    thread = ChatThread.objects.first()
    resp = client.post(reverse('chat-messages', kwargs={'thread_id': str(thread.uuid)}), {'content': 'Hello!'}, format='json')
    assert resp.status_code == 201
    assert resp.data['sender_label'] == 'Visitor'
    assert 'sender' not in resp.data
    assert resp.data['content'] == 'Hello!'


@pytest.mark.django_db
def test_owner_sender_label(client, owner, visitor, car):
    auth(client, 'visitor@example.com')
    client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))
    thread = ChatThread.objects.first()
    auth(client, 'owner@example.com')
    resp = client.post(reverse('chat-messages', kwargs={'thread_id': str(thread.uuid)}), {'content': 'Coming!'}, format='json')
    assert resp.data['sender_label'] == 'Car Owner'


@pytest.mark.django_db
def test_anonymisation_no_real_name(client, visitor, car):
    auth(client, 'visitor@example.com')
    client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))
    thread = ChatThread.objects.first()
    resp = client.get(reverse('chat-messages', kwargs={'thread_id': str(thread.uuid)}))
    for msg in resp.data:
        assert 'sender_id' not in msg
        assert 'sender' not in msg


@pytest.mark.django_db
def test_thread_list_visible_to_both(client, owner, visitor, car):
    visitor_client = APIClient()
    auth(visitor_client, 'visitor@example.com')
    visitor_client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))

    owner_client = APIClient()
    auth(owner_client, 'owner@example.com')
    resp = owner_client.get(reverse('chat-threads'))
    assert resp.status_code == 200
    assert len(resp.data) == 1
