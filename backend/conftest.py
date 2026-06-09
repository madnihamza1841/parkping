"""
Shared pytest fixtures for the full ParkPing test suite.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from cars.models import Car
from chat.models import ChatThread

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def make_user(db):
    def _make(email, password='Pass1234!', full_name='Test User'):
        return User.objects.create_user(email=email, password=password, full_name=full_name)
    return _make


@pytest.fixture
def owner(make_user):
    return make_user('owner@parkping.test')


@pytest.fixture
def visitor(make_user):
    return make_user('visitor@parkping.test')


@pytest.fixture
def car(owner):
    return Car.objects.create(
        owner=owner,
        plate_number='CONF001',
        make='Porsche',
        model='911',
        colour='Silver',
        nickname='Silver Porsche',
    )


@pytest.fixture
def thread(visitor, car):
    return ChatThread.objects.create(scanner=visitor, car=car)


def get_tokens(client, email, password='Pass1234!'):
    resp = client.post(reverse('auth-token'), {'email': email, 'password': password}, format='json')
    return resp.data['access'], resp.data['refresh']


@pytest.fixture
def owner_client(api_client, owner):
    token, _ = get_tokens(api_client, owner.email)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


@pytest.fixture
def visitor_client(make_user, visitor):
    c = APIClient()
    token, _ = get_tokens(c, visitor.email)
    c.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return c
