from app.extensions import db
from app.models import User


def test_register_user(client, app):
    response = client.post(
        "/auth/register",
        data={
            "username": "alice",
            "email": "alice@example.com",
            "password": "study123",
            "password2": "study123",
        },
        follow_redirects=True,
    )

    assert "Аккаунт создан" in response.get_data(as_text=True)

    with app.app_context():
        user = User.query.filter_by(username="alice").first()
        assert user is not None
        assert user.email == "alice@example.com"
        assert user.password_hash != "study123"


def test_login_user(client, app):
    with app.app_context():
        user = User(username="alice", email="alice@example.com")
        user.set_password("study123")
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/auth/login",
        data={"username": "alice", "password": "study123"},
        follow_redirects=True,
    )

    assert "Вы вошли в аккаунт." in response.get_data(as_text=True)


def test_logout_user(client, app):
    with app.app_context():
        user = User(username="alice", email="alice@example.com")
        user.set_password("study123")
        db.session.add(user)
        db.session.commit()

    client.post(
        "/auth/login",
        data={"username": "alice", "password": "study123"},
        follow_redirects=True,
    )

    response = client.get("/auth/logout", follow_redirects=True)
    assert "Вы вышли из аккаунта." in response.get_data(as_text=True)


def test_protected_page_redirects_to_login(client):
    response = client.get("/edit-profile", follow_redirects=True)

    assert "Сначала войдите в аккаунт." in response.get_data(as_text=True)
