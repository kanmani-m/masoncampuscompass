#unit tests
import pytest
import os
from webapp import create_app, db
from flask_login import current_user
from unittest.mock import MagicMock
from webapp.forms import SignUpForm, LoginForm
from wtforms.validators import ValidationError
from webapp.models import User, Interest, Tag, Resource, SavedResource, Favorite, load_user

@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    app = create_app()
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_app_sqlite(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    app = create_app()
    assert "sqlite:///campus_compass.db" in app.config["SQLALCHEMY_DATABASE_URI"]

def test_init_db_exception(monkeypatch, capsys):
    from webapp import db
    def fake():
        raise Exception("boom")
    monkeypatch.setattr(db, "create_all", fake)
    create_app()
    captured = capsys.readouterr()
    assert "Could not initialize database" in captured.out

def test_index(client):
    r = client.get("/")
    assert r.status_code == 200

@pytest.fixture
def fake_user():
    u = MagicMock()
    u.id = 1
    u.username = "alex"
    u.interests = []
    return u

@pytest.fixture
def fake_query(monkeypatch):
    class Query:
        def filter_by(self, **kwargs):
            return self
    from webapp.models import Favorite
    monkeypatch.setattr(Favorite, "query", Query())

def test_dining(client, monkeypatch, fake_query, fake_user):
    from webapp import main
    monkeypatch.setattr(main, "current_user", fake_user)
    response = client.get("/dining")
    assert response.status_code == 302

def test_wellness(client, monkeypatch, fake_query, fake_user):
    from webapp import main
    monkeypatch.setattr(main, "current_user", fake_user)
    response = client.get("/wellness-resources")
    assert response.status_code == 302

def test_career(client, monkeypatch, fake_query, fake_user):
    from webapp import main
    monkeypatch.setattr(main, "current_user", fake_user)
    response = client.get("/career-internship-resources")
    assert response.status_code == 302

def test_academic(client, monkeypatch, fake_query, fake_user):
    from webapp import main
    monkeypatch.setattr(main, "current_user", fake_user)
    response = client.get("/academicResource")
    assert response.status_code == 302

def test_transportation(client, monkeypatch, fake_query, fake_user):
    from webapp import main
    monkeypatch.setattr(main, "current_user", fake_user)
    response = client.get("/transportation")
    assert response.status_code == 302

def test_campus(client, monkeypatch, fake_query, fake_user):
    from webapp import main
    monkeypatch.setattr(main, "current_user", fake_user)
    response = client.get("/campus-events-clubs")
    assert response.status_code == 302

def test_freshman(client, monkeypatch, fake_query, fake_user):
    from webapp import main
    monkeypatch.setattr(main, "current_user", fake_user)
    response = client.get("/freshman-resources")
    assert response.status_code == 302

class Fav:
    def __init__(self, rid):
        self.resource_id = rid

def test_favorites_display(client, monkeypatch):
    from webapp import main
    class Query:
        def all(self):
            return [
                Fav("meal_plans"),
                Fav("fake_resource")
            ]
    from webapp.models import Favorite
    monkeypatch.setattr(Favorite, "query", Query())
    user = type(
        "User",
        (),
        {
            "id": 1,
            "username": "alex",
            "interests": []
        },
    )
    monkeypatch.setattr(main, "current_user", user)
    response = client.get("/favorites")
    assert response.status_code == 302

def test_add_missing_resource(client):
    response = client.post(
        "/add_favorite",
        json={}
    )
    assert response.status_code == 302

def test_add_new_favorite(client, monkeypatch):
    from webapp.models import Favorite
    class Query:
        def filter_by(self, **kwargs):
            return self
    monkeypatch.setattr(Favorite, "query", Query())
    response = client.post(
        "/add_favorite",
        json={
            "resource_id": "meal_plans",
            "resource_type": "dining"
        },
    )
    assert response.status_code == 302

def test_remove_favorite(client, monkeypatch):
    from webapp.models import Favorite
    class Query:
        def filter_by(self, **kwargs):
            return self
    monkeypatch.setattr(Favorite, "query", Query())
    response = client.post(
        "/add_favorite",
        json={
            "resource_id": "meal_plans",
            "resource_type": "dining"
        },
    )
    assert response.status_code == 302

def test_login_form_valid(app):
    """Test LoginForm with valid data."""
    with app.test_request_context():
        form = LoginForm(username="alex", password="securepassword123")
        assert form.validate() is True


def test_login_form_invalid(app):
    """Test LoginForm missing required fields."""
    with app.test_request_context():
        form = LoginForm(username="", password="")
        assert form.validate() is False
        assert "username" in form.errors
        assert "password" in form.errors


def test_signup_form_valid(app, monkeypatch):
    """Test SignUpForm with valid, unique user registration data."""
    from webapp.models import User
    class EmptyQuery:
        def filter_by(self, **kwargs):
            return self
        def first(self):
            return None
    monkeypatch.setattr(User, "query", EmptyQuery())
    with app.test_request_context():
        form = SignUpForm(
            username="newuser",
            password="password123",
            confirm_password="password123",
            interests=["academic_resources", "dining_services"]
        )
        assert form.validate() is True


def test_signup_form_passwords_mismatch(app):
    """Test SignUpForm validation fails when passwords do not match."""
    with app.test_request_context():
        form = SignUpForm(
            username="newuser",
            password="password123",
            confirm_password="differentpassword",
            interests=[]
        )
        assert form.validate() is False
        assert "confirm_password" in form.errors
        assert form.errors["confirm_password"] == ["Passwords must match"]


def test_signup_form_duplicate_username(app, monkeypatch):
    """Test custom validate_username raises ValidationError when username exists."""
    from webapp.models import User
    fake_existing_user = User()
    class ExistingUserQuery:
        def filter_by(self, **kwargs):
            return self
        def first(self):
            return fake_existing_user
    monkeypatch.setattr(User, "query", ExistingUserQuery())
    with app.test_request_context():
        form = SignUpForm(
            username="alex",
            password="password123",
            confirm_password="password123",
            interests=[]
        )
        assert form.validate() is False
        assert "username" in form.errors
        assert "Username already exists. Please choose a different one." in form.errors["username"]

def test_user_repr():
    """Verify that the __repr__ method returns the correctly formatted string."""
    user = User(username="test_user")
    assert repr(user) == "<User test_user>"

def test_login_manager_load_user(app, monkeypatch):
    """Verify that load_user casts the ID to an int and queries the database."""
    mock_query = MagicMock()
    mock_user = User(id=42, username="alex")
    mock_query.get.return_value = mock_user
    monkeypatch.setattr(User, "query", mock_query)
    with app.app_context():
        loaded_user = load_user("42")
        mock_query.get.assert_called_once_with(42)
        assert loaded_user == mock_user
        assert loaded_user.id == 42
        assert loaded_user.username == "alex"


def test_signup_already_authenticated(client, monkeypatch):
    """Covers Line 14: Redirect authenticated user away from signup."""
    mock_user = MagicMock()
    mock_user.is_authenticated = True
    monkeypatch.setattr("flask_login.utils._get_user", lambda: mock_user)

    response = client.get("/signup")
    assert response.status_code == 302
    assert response.headers["Location"] == "/favorites"


def test_login_already_authenticated(client, monkeypatch):
    """Covers Lines 42->39 (or equivalent branch choice): Redirect authenticated user away from login."""
    mock_user = MagicMock()
    mock_user.is_authenticated = True
    monkeypatch.setattr("flask_login.utils._get_user", lambda: mock_user)
    response = client.get("/login")
    assert response.status_code == 302
    assert response.headers["Location"] == "/favorites"


def test_login_invalid_credentials(client, monkeypatch, app):
    """Covers Line 59: Executes the 'else' block when password check fails."""
    with app.app_context():
        fake_user = User(username="badlogin")
        fake_user.set_password("correct_password")
        class MockUserQuery:
            def filter_by(self, **kwargs):
                return self
            def first(self):
                return fake_user
        monkeypatch.setattr(User, "query", MockUserQuery())
        response = client.post("/login", data={
            "username": "badlogin",
            "password": "wrong_password"
        }, follow_redirects=True)
        assert response.status_code == 200


def test_signup_interest_not_found(client, monkeypatch, app):
    """Covers Lines 26->25 branch jump: Loop proceeds when an interest query returns None."""
    with app.app_context():
        class EmptyUserQuery:
            def filter_by(self, **kwargs):
                return self
            def first(self):
                return None
        monkeypatch.setattr(User, "query", EmptyUserQuery())
        class EmptyInterestQuery:
            def filter_by(self, **kwargs):
                return self
            def first(self):
                return None
        monkeypatch.setattr(Interest, "query", EmptyInterestQuery())
        response = client.post("/signup", data={
            "username": "uniquename",
            "password": "password123",
            "confirm_password": "password123",
            "interests": ["academic_resources"]
        })
        assert response.status_code == 302
        assert response.headers["Location"] == "/login"


def test_logout_route(client, monkeypatch, app):
    """Covers Lines 81-83: Executes full logout function lifecycle."""
    mock_user = MagicMock()
    mock_user.is_authenticated = True
    monkeypatch.setattr("flask_login.utils._get_user", lambda: mock_user)
    mock_logout = MagicMock()
    monkeypatch.setattr("webapp.auth.logout_user", mock_logout)
    response = client.get("/logout")
    mock_logout.assert_called_once()
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

def test_signup_populates_missing_interests(client, monkeypatch, app):
    """Test that signup route seeds missing interests into the database."""
    with app.app_context():
        added_interests = []
        class MockInterestQuery:
            def filter_by(self, name):
                self.current_name = name
                return self
            def first(self):
                if self.current_name == "academic_resources":
                    return None
                return MagicMock()
        monkeypatch.setattr(Interest, "query", MockInterestQuery())
        monkeypatch.setattr(db.session, "add", lambda obj: added_interests.append(obj))
        monkeypatch.setattr(db.session, "commit", lambda: None)
        response = client.get("/signup")
        assert response.status_code == 200
        assert len(added_interests) == 1
        assert isinstance(added_interests[0], Interest)
        assert added_interests[0].name == "academic_resources"