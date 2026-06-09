"""
Integration test: scan → chat → call token full flow.
Ensures the end-to-end path works and no PII leaks across any step.
"""
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_full_scan_chat_call_flow(visitor_client, owner_client, car, owner):
    car_uuid = str(car.uuid)

    # 1. Visitor scans the QR → public endpoint, no auth required
    from rest_framework.test import APIClient
    anon = APIClient()
    scan = anon.get(reverse('car-scan', kwargs={'car_uuid': car_uuid}))
    assert scan.status_code == 200
    assert set(scan.data.keys()) == {'uuid', 'nickname', 'make', 'model'}

    # 2. Visitor starts a chat
    start = visitor_client.post(reverse('chat-start', kwargs={'car_uuid': car_uuid}))
    assert start.status_code == 201
    thread_id = start.data['uuid']

    # 3. Visitor sends a message — sender_label must be 'Visitor', no PII
    msg = visitor_client.post(
        reverse('chat-messages', kwargs={'thread_id': thread_id}),
        {'content': 'Please move your car!'},
        format='json',
    )
    assert msg.status_code == 201
    assert msg.data['sender_label'] == 'Visitor'
    assert 'sender' not in msg.data

    # 4. Owner replies — sender_label must be 'Car Owner'
    owner_msg = owner_client.post(
        reverse('chat-messages', kwargs={'thread_id': thread_id}),
        {'content': 'On my way!'},
        format='json',
    )
    assert owner_msg.status_code == 201
    assert owner_msg.data['sender_label'] == 'Car Owner'

    # 5. Visitor requests a call token
    call = visitor_client.post(reverse('call-token', kwargs={'car_uuid': car_uuid}))
    assert call.status_code == 201
    assert 'channel_id' in call.data
    assert 'token' in call.data

    # 6. Simulate owner declining
    channel_id = call.data['channel_id']
    decline = visitor_client.post(
        reverse('call-status', kwargs={'channel_id': channel_id}),
        {'status': 'declined'},
        format='json',
    )
    assert decline.status_code == 200

    # 7. System message should appear in thread
    msgs = visitor_client.get(reverse('chat-messages', kwargs={'thread_id': thread_id}))
    system_msgs = [m for m in msgs.data if m.get('is_system')]
    assert len(system_msgs) >= 1
    assert 'declined' in system_msgs[0]['content']
