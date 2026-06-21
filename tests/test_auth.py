from app.models import User


def test_register_login_and_logout_flow(client, app):
    response = client.post(
        "/auth/register",
        data={
            "username": "alice",
            "password": "study123",
            "password2": "study123",
        },
        follow_redirects=True,
    )

    assert "Аккаунт создан" in response.get_data(as_text=True)

    with app.app_context():
        assert User.query.filter_by(username="alice").first() is not None

    response = client.post(
        "/auth/login",
        data={"username": "alice", "password": "study123"},
        follow_redirects=True,
    )
    assert "Вы вошли в аккаунт." in response.get_data(as_text=True)

    response = client.get("/auth/logout", follow_redirects=True)
    assert "Вы вышли из аккаунта." in response.get_data(as_text=True)
