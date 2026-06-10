"""Tests for 24-hour chat expiry and user blocking."""
from datetime import timedelta
import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from cars.models import Car
from chat.models import ChatThread, Message, Block

User = get_user_model()


@pytest.fixture
def owner(db):
    return User.objects.create_user(email='owner@bx.test', password='Pass1234!', full_name='Owner')


@pytest.fixture
def visitor(db):
    return User.objects.create_user(email='visitor@bx.test', password='Pass1234!', full_name='Visitor')


@pytest.fixture
def car(owner):
    return Car.objects.create(owner=owner, plate_number='BX001', make='VW',
                              model='Golf', colour='Grey', nickname='Grey Golf')


@pytest.fixture
def thread(visitor, car):
    return ChatThread.objects.create(scanner=visitor, car=car)


def make_client(email):
    c = APIClient()
    r = c.post(reverse('auth-token'), {'email': email, 'password': 'Pass1234!'}, format='json')
    c.credentials(HTTP_AUTHORIZATION='Bearer ' + r.data['access'])
    return c


@pytest.fixture
def visitor_client(visitor):
    return make_client('visitor@bx.test')


@pytest.fixture
def owner_client(owner):
    return make_client('owner@bx.test')


def age_message(msg, hours):
    """Backdate a message (auto_now_add can't be set at create time)."""
    Message.objects.filter(pk=msg.pk).update(timestamp=timezone.now() - timedelta(hours=hours))


def age_thread(t, hours):
    ChatThread.objects.filter(pk=t.pk).update(created_at=timezone.now() - timedelta(hours=hours))


# ── 24h expiry ────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_fresh_messages_visible(visitor_client, thread, visitor):
    Message.objects.create(thread=thread, sender=visitor, content='hello')
    resp = visitor_client.get(reverse('chat-messages', kwargs={'thread_id': str(thread.uuid)}))
    assert len(resp.data) == 1


@pytest.mark.django_db
def test_messages_disappear_after_24h(visitor_client, thread, visitor):
    old = Message.objects.create(thread=thread, sender=visitor, content='old message')
    age_message(old, hours=25)
    fresh = Message.objects.create(thread=thread, sender=visitor, content='fresh message')

    resp = visitor_client.get(reverse('chat-messages', kwargs={'thread_id': str(thread.uuid)}))
    contents = [m['content'] for m in resp.data]
    assert 'fresh message' in contents
    assert 'old message' not in contents


@pytest.mark.django_db
def test_message_at_23h_still_visible(visitor_client, thread, visitor):
    msg = Message.objects.create(thread=thread, sender=visitor, content='almost expired')
    age_message(msg, hours=23)
    resp = visitor_client.get(reverse('chat-messages', kwargs={'thread_id': str(thread.uuid)}))
    assert len(resp.data) == 1


@pytest.mark.django_db
def test_thread_disappears_from_list_after_24h_inactivity(visitor_client, thread, visitor):
    msg = Message.objects.create(thread=thread, sender=visitor, content='hi')
    age_message(msg, hours=25)
    age_thread(thread, hours=30)

    resp = visitor_client.get(reverse('chat-threads'))
    assert len(resp.data) == 0


@pytest.mark.django_db
def test_thread_stays_visible_with_recent_message(visitor_client, thread, visitor):
    age_thread(thread, hours=48)  # old thread...
    Message.objects.create(thread=thread, sender=visitor, content='new activity')  # ...but fresh message

    resp = visitor_client.get(reverse('chat-threads'))
    assert len(resp.data) == 1


@pytest.mark.django_db
def test_new_empty_thread_visible(visitor_client, thread):
    # No messages at all — visible because created_at is fresh
    resp = visitor_client.get(reverse('chat-threads'))
    assert len(resp.data) == 1


@pytest.mark.django_db
def test_expired_message_hidden_from_thread_preview(visitor_client, thread, visitor):
    old = Message.objects.create(thread=thread, sender=visitor, content='expired preview')
    age_message(old, hours=25)

    resp = visitor_client.get(reverse('chat-threads'))
    assert len(resp.data) == 1  # thread itself young enough (created_at fresh)
    assert resp.data[0]['last_message'] is None  # but expired message not previewed


@pytest.mark.django_db
def test_thread_serializer_includes_expires_at(visitor_client, thread):
    resp = visitor_client.get(reverse('chat-threads'))
    assert 'expires_at' in resp.data[0]


# ── Blocking ──────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_owner_blocks_visitor(owner_client, thread):
    resp = owner_client.post(reverse('chat-block', kwargs={'thread_id': str(thread.uuid)}))
    assert resp.status_code == 200
    assert Block.objects.count() == 1


@pytest.mark.django_db
def test_blocked_visitor_cannot_send_message(owner_client, visitor_client, thread):
    owner_client.post(reverse('chat-block', kwargs={'thread_id': str(thread.uuid)}))
    resp = visitor_client.post(
        reverse('chat-messages', kwargs={'thread_id': str(thread.uuid)}),
        {'content': 'let me in'}, format='json')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_blocker_also_cannot_send(owner_client, thread):
    """Blocking cuts the conversation both ways."""
    owner_client.post(reverse('chat-block', kwargs={'thread_id': str(thread.uuid)}))
    resp = owner_client.post(
        reverse('chat-messages', kwargs={'thread_id': str(thread.uuid)}),
        {'content': 'still talking?'}, format='json')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_blocked_visitor_cannot_start_new_chat(owner_client, visitor_client, thread, car):
    owner_client.post(reverse('chat-block', kwargs={'thread_id': str(thread.uuid)}))
    resp = visitor_client.post(reverse('chat-start', kwargs={'car_uuid': str(car.uuid)}))
    assert resp.status_code == 403


@pytest.mark.django_db
def test_blocked_visitor_cannot_call(owner_client, visitor_client, thread, car):
    owner_client.post(reverse('chat-block', kwargs={'thread_id': str(thread.uuid)}))
    resp = visitor_client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    assert resp.status_code == 403


@pytest.mark.django_db
def test_unblock_restores_contact(owner_client, visitor_client, thread, car):
    owner_client.post(reverse('chat-block', kwargs={'thread_id': str(thread.uuid)}))
    owner_client.post(reverse('chat-unblock', kwargs={'thread_id': str(thread.uuid)}))

    resp = visitor_client.post(
        reverse('chat-messages', kwargs={'thread_id': str(thread.uuid)}),
        {'content': 'we are friends again'}, format='json')
    assert resp.status_code == 201

    resp = visitor_client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    assert resp.status_code == 201


@pytest.mark.django_db
def test_block_is_idempotent(owner_client, thread):
    owner_client.post(reverse('chat-block', kwargs={'thread_id': str(thread.uuid)}))
    resp = owner_client.post(reverse('chat-block', kwargs={'thread_id': str(thread.uuid)}))
    assert resp.status_code == 200
    assert Block.objects.count() == 1


@pytest.mark.django_db
def test_visitor_can_block_owner_too(visitor_client, owner_client, thread):
    visitor_client.post(reverse('chat-block', kwargs={'thread_id': str(thread.uuid)}))
    resp = owner_client.post(
        reverse('chat-messages', kwargs={'thread_id': str(thread.uuid)}),
        {'content': 'hello?'}, format='json')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_third_party_cannot_block_on_others_thread(thread, db):
    User.objects.create_user(email='stranger@bx.test', password='Pass1234!', full_name='Stranger')
    stranger = make_client('stranger@bx.test')
    resp = stranger.post(reverse('chat-block', kwargs={'thread_id': str(thread.uuid)}))
    assert resp.status_code == 403


@pytest.mark.django_db
def test_thread_serializer_block_flags(owner_client, visitor_client, thread):
    owner_client.post(reverse('chat-block', kwargs={'thread_id': str(thread.uuid)}))

    owner_threads = owner_client.get(reverse('chat-threads')).data
    assert owner_threads[0]['blocked_by_me'] is True
    assert owner_threads[0]['is_blocked'] is True

    visitor_threads = visitor_client.get(reverse('chat-threads')).data
    assert visitor_threads[0]['blocked_by_me'] is False  # visitor didn't block
    assert visitor_threads[0]['is_blocked'] is True      # but a block exists


@pytest.mark.django_db
def test_block_response_contains_no_pii(owner_client, thread):
    resp = owner_client.post(reverse('chat-block', kwargs={'thread_id': str(thread.uuid)}))
    body = str(resp.data)
    assert 'visitor@bx.test' not in body
    assert 'Visitor' not in body  # not even the full_name


# ── Call status security (fixed during E2E testing) ──────────────────────────

@pytest.mark.django_db
def test_stranger_cannot_update_call_status(visitor_client, car, db):
    resp = visitor_client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    channel_id = resp.data['channel_id']

    User.objects.create_user(email='callsnoop@bx.test', password='Pass1234!', full_name='Snoop')
    snoop = make_client('callsnoop@bx.test')
    resp = snoop.post(reverse('call-status', kwargs={'channel_id': channel_id}),
                      {'status': 'declined'}, format='json')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_participants_can_update_call_status(visitor_client, owner_client, car):
    resp = visitor_client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    channel_id = resp.data['channel_id']
    resp = owner_client.post(reverse('call-status', kwargs={'channel_id': channel_id}),
                             {'status': 'answered'}, format='json')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_owner_cannot_call_own_car(owner_client, car):
    resp = owner_client.post(reverse('call-token', kwargs={'car_uuid': str(car.uuid)}))
    assert resp.status_code == 400
