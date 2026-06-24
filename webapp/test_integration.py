#integration tests
import pytest

from webapp import create_app, db
from webapp.models import (
    User,
    Interest,
    Favorite,
    Tag,
    Resource,
    SavedResource,
    load_user,
)


@pytest.fixture
def app(monkeypatch, tmp_path):
    db_file = tmp_path / "integration.sqlite3"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file.as_posix()}")

    app = create_app()
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def signup(client, username="int_user", password="Password123!", interests=None):
    if interests is None:
        interests = ["academic_resources", "dining_services"]
    return client.post(
        "/signup",
        data={
            "username": username,
            "password": password,
            "confirm_password": password,
            "interests": interests,
        },
        follow_redirects=True,
    )


def login(client, username="int_user", password="Password123!", follow_redirects=True):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=follow_redirects,
    )


def test_public_pages_load(client):
    assert client.get("/").status_code == 200
    assert client.get("/signup").status_code == 200
    assert client.get("/login").status_code == 200


def test_signup_get_seeds_interests_once(client, app):
    client.get("/signup")
    client.get("/signup")

    with app.app_context():
        names = {i.name for i in Interest.query.all()}
        assert len(names) == 6
        assert "academic_resources" in names
        assert "campus_events" in names


def test_signup_login_logout_happy_path(client, app):
    r_signup = signup(client)
    assert r_signup.status_code == 200

    with app.app_context():
        user = User.query.filter_by(username="int_user").first()
        assert user is not None
        assert user.password_hash != "Password123!"
        assert user.check_password("Password123!")
        assert not user.check_password("WrongPassword!")
        assert "int_user" in repr(user)

    r_login = login(client)
    assert r_login.status_code == 200

    r_favorites = client.get("/favorites")
    assert r_favorites.status_code == 200

    r_logout = client.get("/logout", follow_redirects=True)
    assert r_logout.status_code == 200

    r_after_logout = client.get("/favorites", follow_redirects=False)
    assert r_after_logout.status_code in (302, 401)


def test_authenticated_user_redirected_from_signup_and_login(client):
    signup(client, username="already_in")
    login(client, username="already_in", follow_redirects=True)

    r_signup = client.get("/signup", follow_redirects=False)
    r_login = client.get("/login", follow_redirects=False)

    assert r_signup.status_code == 302
    assert "/favorites" in r_signup.headers.get("Location", "")
    assert r_login.status_code == 302
    assert "/favorites" in r_login.headers.get("Location", "")


def test_duplicate_signup_rejected(client, app):
    signup(client, username="dup_user")
    signup(client, username="dup_user")

    with app.app_context():
        users = User.query.filter_by(username="dup_user").all()
        assert len(users) == 1


def test_invalid_login_does_not_authenticate(client):
    signup(client, username="bad_login_user")

    r_bad = login(client, username="bad_login_user", password="WrongPassword!", follow_redirects=True)
    assert r_bad.status_code == 200

    r_favorites = client.get("/favorites", follow_redirects=False)
    assert r_favorites.status_code in (302, 401)


def test_dashboard_redirect_for_authenticated_user(client):
    signup(client, username="dash_user")
    login(client, username="dash_user")

    r = client.get("/dashboard", follow_redirects=False)
    assert r.status_code == 302
    assert "/favorites" in r.headers.get("Location", "")


def test_protected_routes_require_auth_then_allow_after_login(client):
    protected_routes = [
        "/favorites",
        "/academicResource",
        "/dining",
        "/transportation",
        "/campus-events-clubs",
        "/wellness-resources",
        "/career-internship-resources",
        "/transfer-resources",
        "/freshman-resources",
    ]

    for route in protected_routes:
        r = client.get(route, follow_redirects=False)
        assert r.status_code in (302, 401)

    signup(client, username="route_user")
    login(client, username="route_user")

    for route in protected_routes:
        r = client.get(route, follow_redirects=False)
        assert r.status_code == 200


def test_add_favorite_missing_resource_id_returns_400(client):
    signup(client, username="missing_id_user")
    login(client, username="missing_id_user")

    r = client.post("/add_favorite", json={})
    assert r.status_code == 400
    payload = r.get_json()
    assert payload["success"] is False


def test_add_and_remove_favorite_toggle(client, app):
    signup(client, username="fav_user")
    login(client, username="fav_user")

    r_add = client.post(
        "/add_favorite",
        json={"resource_id": "meal_plans", "resource_type": "dining"},
    )
    assert r_add.status_code == 200
    assert r_add.get_json()["success"] is True

    with app.app_context():
        user = User.query.filter_by(username="fav_user").first()
        row = Favorite.query.filter_by(
            user_id=user.id,
            resource_id="meal_plans",
            resource_type="dining",
        ).first()
        assert row is not None

    r_remove = client.post(
        "/add_favorite",
        json={"resource_id": "meal_plans", "resource_type": "dining"},
    )
    assert r_remove.status_code == 200
    assert r_remove.get_json()["success"] is True

    with app.app_context():
        user = User.query.filter_by(username="fav_user").first()
        row = Favorite.query.filter_by(
            user_id=user.id,
            resource_id="meal_plans",
            resource_type="dining",
        ).first()
        assert row is None


def test_favorites_aggregation_and_unknown_ids_not_rendered(client, app):
    signup(client, username="agg_user")
    login(client, username="agg_user")

    with app.app_context():
        user = User.query.filter_by(username="agg_user").first()
        db.session.add_all(
            [
                Favorite(user_id=user.id, resource_id="meal_plans", resource_type="dining"),
                Favorite(user_id=user.id, resource_id="student_health_services", resource_type="wellness"),
                Favorite(user_id=user.id, resource_id="find_job", resource_type="career"),
                Favorite(user_id=user.id, resource_id="academicResource1", resource_type="academic"),
                Favorite(user_id=user.id, resource_id="mason_commutes", resource_type="transportation"),
                Favorite(user_id=user.id, resource_id="mason360_student_orgs", resource_type="campus_events_clubs"),
                Favorite(user_id=user.id, resource_id="general_transfer_student_resources", resource_type="transfer"),
                Favorite(user_id=user.id, resource_id="freshmanResource1", resource_type="freshman"),
                Favorite(user_id=user.id, resource_id="not_in_map", resource_type="dining"),
            ]
        )
        db.session.commit()

    r = client.get("/favorites")
    assert r.status_code == 200
    page = r.get_data(as_text=True)

    assert "Meal Plans" in page
    assert "Student Health Services" in page
    assert "Find a Job" in page
    assert "Math Tutoring" in page
    assert "Mason Commutes" in page
    assert "Mason360" in page
    assert "General Transfer Student Resources" in page
    assert "New College-Student Resources" in page
    assert "not_in_map" not in page


def test_add_favorite_db_exception_returns_500(client, monkeypatch):
    signup(client, username="err_user")
    login(client, username="err_user")

    def boom():
        raise Exception("forced-db-error")

    monkeypatch.setattr(db.session, "commit", boom)

    r = client.post(
        "/add_favorite",
        json={"resource_id": "meal_plans", "resource_type": "dining"},
    )
    assert r.status_code == 500
    payload = r.get_json()
    assert payload["success"] is False
    assert "forced-db-error" in payload["message"]


def test_user_loader_and_extra_model_relationships(app):
    with app.app_context():
        u = User(username="model_user")
        u.set_password("Password123!")
        db.session.add(u)

        t = Tag(name="study")
        r = Resource(
            title="Library",
            description="Quiet place",
            url="https://example.com/library",
        )
        r.tags.append(t)
        db.session.add_all([t, r])
        db.session.flush()

        sr = SavedResource(user_id=u.id, resource_id=r.id)
        db.session.add(sr)
        db.session.commit()

        loaded = load_user(u.id)
        assert loaded is not None
        assert loaded.username == "model_user"

        saved = SavedResource.query.filter_by(user_id=u.id).first()
        assert saved is not None
        assert saved.user.username == "model_user"
        assert saved.resource.title == "Library"
        assert saved.resource.tags[0].name == "study"