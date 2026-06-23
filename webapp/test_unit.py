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