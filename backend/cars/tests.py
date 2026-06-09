import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from cars.models import Car

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(email='owner@example.com', password='Pass1234!', full_name='Owner')


@pytest.fixture
def auth_client(client, user):
    resp = client.post(reverse('auth-token'), {'email': 'owner@example.com', 'password': 'Pass1234!'}, format='json')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data['access'])
    return client


@pytest.fixture
def car(user):
    return Car.objects.create(
        owner=user,
        plate_number='ABC123',
        make='Toyota',
        model='Corolla',
        colour='White',
        nickname='My White Car',
    )


@pytest.mark.django_db
def test_create_car(auth_client):
    resp = auth_client.post(reverse('car-list'), {
        'plate_number': 'XYZ999',
        'make': 'Honda',
        'model': 'Civic',
        'colour': 'Blue',
        'nickname': 'Blue Civic',
    }, format='json')
    assert resp.status_code == 201
    assert 'uuid' in resp.data


@pytest.mark.django_db
def test_list_cars(auth_client, car):
    resp = auth_client.get(reverse('car-list'))
    assert resp.status_code == 200
    assert len(resp.data) == 1


@pytest.mark.django_db
def test_car_detail(auth_client, car):
    resp = auth_client.get(reverse('car-detail', kwargs={'uuid': str(car.uuid)}))
    assert resp.status_code == 200
    assert resp.data['plate_number'] == 'ABC123'


@pytest.mark.django_db
def test_car_qr_image(auth_client, car):
    resp = auth_client.get(reverse('car-qr', kwargs={'uuid': str(car.uuid)}))
    assert resp.status_code == 200
    assert resp['Content-Type'] == 'image/png'


@pytest.mark.django_db
def test_car_qr_pdf(auth_client, car):
    resp = auth_client.get(reverse('car-qr-pdf', kwargs={'uuid': str(car.uuid)}))
    assert resp.status_code == 200
    assert resp['Content-Type'] == 'application/pdf'


@pytest.mark.django_db
def test_scan_returns_no_pii(db, client, car):
    resp = client.get(reverse('car-scan', kwargs={'car_uuid': str(car.uuid)}))
    assert resp.status_code == 200
    assert set(resp.data.keys()) == {'uuid', 'nickname', 'make', 'model'}
    assert 'owner' not in resp.data
    assert 'plate_number' not in resp.data
    assert 'colour' not in resp.data


@pytest.mark.django_db
def test_scan_unknown_car(db, client):
    import uuid
    resp = client.get(reverse('car-scan', kwargs={'car_uuid': str(uuid.uuid4())}))
    assert resp.status_code == 404
