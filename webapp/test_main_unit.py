import pytest
from webapp import create_app, db


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


def login_user(client):
    client.post('/signup', data={
        'username': 'mainuser',
        'password': 'Password123!',
        'confirm_password': 'Password123!',
        'interests': ['academic_resources']
    }, follow_redirects=True)

    client.post('/login', data={
        'username': 'mainuser',
        'password': 'Password123!'
    }, follow_redirects=True)


def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200


def test_favorites_requires_login(client):
    response = client.get('/favorites')
    assert response.status_code in [302, 401]


def test_dining_page_logged_in(client):
    login_user(client)
    response = client.get('/dining')
    assert response.status_code == 200


def test_transportation_page_logged_in(client):
    login_user(client)
    response = client.get('/transportation')
    assert response.status_code == 200


def test_career_page_logged_in(client):
    login_user(client)
    response = client.get('/career-internship-resources')
    assert response.status_code == 200


def test_wellness_page_logged_in(client):
    login_user(client)
    response = client.get('/wellness-resources')
    assert response.status_code == 200


def test_academic_page_logged_in(client):
    login_user(client)
    response = client.get('/academicResource')
    assert response.status_code == 200


def test_campus_events_page_logged_in(client):
    login_user(client)
    response = client.get('/campus-events-clubs')
    assert response.status_code == 200






def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_signup_page(client):
    response = client.get("/signup")
    assert response.status_code == 200


def test_favorites_requires_login(client):
    response = client.get("/favorites", follow_redirects=False)
    assert response.status_code in [302, 401, 403]


def test_dining_redirect_or_loads(client):
    response = client.get("/dining", follow_redirects=False)
    assert response.status_code in [200, 302]


def test_transportation_redirect_or_loads(client):
    response = client.get("/transportation", follow_redirects=False)
    assert response.status_code in [200, 302]


def test_transfer_redirect_or_loads(client):
    response = client.get("/transfer", follow_redirects=False)
    assert response.status_code in [200, 302]


def test_logout_redirects(client):
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code in [302, 401]


def test_bad_page_404(client):
    response = client.get("/this-page-does-not-exist")
    assert response.status_code == 404