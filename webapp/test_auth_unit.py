import pytest
from webapp import create_app, db
from webapp.models import User


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_signup_page_loads(client):
    response = client.get('/signup')
    assert response.status_code == 200


def test_login_page_loads(client):
    response = client.get('/login')
    assert response.status_code == 200


def test_valid_signup_creates_user(client, app):
    response = client.post('/signup', data={
        'username': 'testuser',
        'password': 'Password123!',
        'confirm_password': 'Password123!',
        'interests': ['academic_resources']
    }, follow_redirects=True)

    with app.app_context():
        user = User.query.filter_by(username='testuser').first()

    assert user is not None
    assert response.status_code == 200


def test_invalid_signup_missing_username(client):
    response = client.post('/signup', data={
        'username': '',
        'password': 'Password123!',
        'confirm_password': 'Password123!',
        'interests': ['academic_resources']
    }, follow_redirects=True)

    assert response.status_code == 200


def test_valid_login(client):
    client.post('/signup', data={
        'username': 'loginuser',
        'password': 'Password123!',
        'confirm_password': 'Password123!',
        'interests': ['academic_resources']
    }, follow_redirects=True)

    response = client.post('/login', data={
        'username': 'loginuser',
        'password': 'Password123!'
    }, follow_redirects=True)

    assert response.status_code == 200


def test_invalid_login_wrong_password(client):
    client.post('/signup', data={
        'username': 'wrongpass',
        'password': 'Password123!',
        'confirm_password': 'Password123!',
        'interests': ['academic_resources']
    }, follow_redirects=True)

    response = client.post('/login', data={
        'username': 'wrongpass',
        'password': 'WrongPassword!'
    }, follow_redirects=True)

    assert response.status_code == 200


def test_logout_redirects(client):
    response = client.get('/logout', follow_redirects=False)
    assert response.status_code in [302, 401]

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200






