#unit tests
import pytest
import os
from webapp import create_app
from unittest.mock import MagicMock

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

def fake_favorites():
    return []

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
        def all(self):
            return []
        def first(self):
            return None
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

def test_favorites(client, monkeypatch, fake_query, fake_user):
    from webapp import main
    monkeypatch.setattr(main, "current_user", fake_user)
    response = client.get("/favorites")
    assert response.status_code == 302

class Fav:
    def __init__(self, rid):
        self.resource_id = rid

def test_favorites_display(client, monkeypatch):
    from webapp import main
    class Query:
        def filter_by(self, **kwargs):
            return self
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
        def first(self):
            return None
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
        def first(self):
            return Favorite()
    monkeypatch.setattr(Favorite, "query", Query())
    response = client.post(
        "/add_favorite",
        json={
            "resource_id": "meal_plans",
            "resource_type": "dining"
        },
    )
    assert response.status_code == 302

