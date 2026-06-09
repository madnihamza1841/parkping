import uuid
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from cars.models import Car

User = get_user_model()

CAR_FIELDS = {'uuid', 'nickname', 'make', 'model'}
OWNER_PII_FIELDS = {'owner', 'plate_number', 'colour', 'variant'}


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(email='owner@example.com', password='Pass1234!', full_name='Owner')


@pytest.fixture
def other_user(db):
    return User.objects.create_user(email='other@example.com', password='Pass1234!', full_name='Other')


def _auth(client, email, password='Pass1234!'):
    resp = client.post(reverse('auth-token'), {'email': email, 'password': password}, format='json')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data['access'])
    return client


@pytest.fixture
def auth_client(client, user):
    return _auth(client, 'owner@example.com')


@pytest.fixture
def car(user):
    return Car.objects.create(owner=user, plate_number='ABC123', make='Toyota',
                              model='Corolla', colour='White', nickname='My White Car')


@pytest.fixture
def other_car(other_user):
    return Car.objects.create(owner=other_user, plate_number='XYZ789', make='Honda',
                              model='Civic', colour='Red', nickname='Red Civic')


# ── CRUD ─────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_create_car(auth_client):
    resp = auth_client.post(reverse('car-list'), {
        'plate_number': 'NEW001', 'make': 'Honda', 'model': 'Civic',
        'colour': 'Blue', 'nickname': 'Blue Civic',
    }, format='json')
    assert resp.status_code == 201
    assert 'uuid' in resp.data


@pytest.mark.django_db
def test_create_car_duplicate_plate(auth_client, car):
    resp = auth_client.post(reverse('car-list'), {
        'plate_number': 'ABC123', 'make': 'BMW', 'model': '3',
        'colour': 'Black', 'nickname': 'Second Car',
    }, format='json')
    assert resp.status_code == 400


@pytest.mark.django_db
def test_create_car_requires_auth(client, db):
    resp = client.post(reverse('car-list'), {'plate_number': 'X', 'make': 'Y', 'model': 'Z', 'colour': 'W', 'nickname': 'N'}, format='json')
    assert resp.status_code == 401


@pytest.mark.django_db
def test_list_cars_only_own(auth_client, car, other_car):
    resp = auth_client.get(reverse('car-list'))
    assert resp.status_code == 200
    uuids = [c['uuid'] for c in resp.data]
    assert str(car.uuid) in uuids
    assert str(other_car.uuid) not in uuids  # never returns another user's cars


@pytest.mark.django_db
def test_car_detail(auth_client, car):
    resp = auth_client.get(reverse('car-detail', kwargs={'uuid': str(car.uuid)}))
    assert resp.status_code == 200
    assert resp.data['plate_number'] == 'ABC123'


@pytest.mark.django_db
def test_car_detail_other_user_gets_404(client, other_user, car):
    _auth(client, 'other@example.com')
    resp = client.get(reverse('car-detail', kwargs={'uuid': str(car.uuid)}))
    assert resp.status_code == 404  # not 403 — owner identity not leaked


@pytest.mark.django_db
def test_delete_car(auth_client, car):
    resp = auth_client.delete(reverse('car-detail', kwargs={'uuid': str(car.uuid)}))
    assert resp.status_code == 204
    assert Car.objects.filter(uuid=car.uuid).count() == 0


@pytest.mark.django_db
def test_delete_other_users_car_is_404(client, other_user, car):
    _auth(client, 'other@example.com')
    resp = client.delete(reverse('car-detail', kwargs={'uuid': str(car.uuid)}))
    assert resp.status_code == 404
    assert Car.objects.filter(uuid=car.uuid).exists()


@pytest.mark.django_db
def test_patch_car(auth_client, car):
    resp = auth_client.patch(reverse('car-detail', kwargs={'uuid': str(car.uuid)}),
                              {'nickname': 'Updated Nick'}, format='json')
    assert resp.status_code == 200
    assert resp.data['nickname'] == 'Updated Nick'


# ── QR / PDF ─────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_car_qr_image(auth_client, car):
    resp = auth_client.get(reverse('car-qr', kwargs={'uuid': str(car.uuid)}))
    assert resp.status_code == 200
    assert resp['Content-Type'] == 'image/png'
    assert len(resp.content) > 100  # actual PNG bytes


@pytest.mark.django_db
def test_car_qr_pdf(auth_client, car):
    resp = auth_client.get(reverse('car-qr-pdf', kwargs={'uuid': str(car.uuid)}))
    assert resp.status_code == 200
    assert resp['Content-Type'] == 'application/pdf'
    assert resp.content[:4] == b'%PDF'  # valid PDF header


@pytest.mark.django_db
def test_qr_requires_auth(client, db, car):
    resp = client.get(reverse('car-qr', kwargs={'uuid': str(car.uuid)}))
    assert resp.status_code == 401


@pytest.mark.django_db
def test_qr_other_user_gets_404(client, other_user, car):
    _auth(client, 'other@example.com')
    resp = client.get(reverse('car-qr', kwargs={'uuid': str(car.uuid)}))
    assert resp.status_code == 404


# ── Public scan endpoint — PII enforcement ────────────────────────────────────

@pytest.mark.django_db
def test_scan_returns_only_allowed_fields(db, client, car):
    resp = client.get(reverse('car-scan', kwargs={'car_uuid': str(car.uuid)}))
    assert resp.status_code == 200
    assert set(resp.data.keys()) == CAR_FIELDS
    for pii in OWNER_PII_FIELDS:
        assert pii not in resp.data


@pytest.mark.django_db
def test_scan_no_auth_required(db, client, car):
    # Completely unauthenticated request must succeed
    resp = client.get(reverse('car-scan', kwargs={'car_uuid': str(car.uuid)}))
    assert resp.status_code == 200


@pytest.mark.django_db
def test_scan_unknown_uuid_returns_404(db, client):
    resp = client.get(reverse('car-scan', kwargs={'car_uuid': str(uuid.uuid4())}))
    assert resp.status_code == 404


@pytest.mark.django_db
def test_scan_does_not_expose_owner_identity(db, client, car):
    resp = client.get(reverse('car-scan', kwargs={'car_uuid': str(car.uuid)}))
    # Flatten the whole response body and search for owner's email
    body = str(resp.data)
    assert 'owner@example.com' not in body
    assert 'Pass1234' not in body
    assert 'ABC123' not in body  # plate_number is PII in scan context
