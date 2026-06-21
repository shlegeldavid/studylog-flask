from app.extensions import db
from app.models import Post, User


def login(client, username: str, password: str) -> None:
    client.post(
        "/auth/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def test_authenticated_user_can_create_post(client, app):
    with app.app_context():
        user = User(username="alice")
        user.set_password("study123")
        db.session.add(user)
        db.session.commit()

    login(client, "alice", "study123")
    response = client.post("/", data={"body": "Первая заметка"}, follow_redirects=True)

    assert "Заметка опубликована." in response.get_data(as_text=True)
    assert "Первая заметка" in response.get_data(as_text=True)

    with app.app_context():
        assert Post.query.count() == 1


def test_followed_feed_shows_notes_of_followed_users(client, app):
    with app.app_context():
        alice = User(username="alice")
        alice.set_password("study123")
        bob = User(username="bob")
        bob.set_password("study123")
        db.session.add_all([alice, bob])
        db.session.commit()

        alice.follow(bob)
        db.session.add(
            Post(body="Конспект по Flask", author=bob)
        )
        db.session.commit()

    login(client, "alice", "study123")
    response = client.get("/", follow_redirects=True)

    assert "Конспект по Flask" in response.get_data(as_text=True)
