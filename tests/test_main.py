from datetime import UTC, datetime, timedelta

from app.extensions import db
from app.models import Post, User


def login(client, username: str, password: str) -> None:
    client.post(
        "/auth/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def add_posts(author: User, prefix: str, count: int) -> None:
    start = datetime.now(UTC).replace(tzinfo=None)
    for index in range(count):
        db.session.add(
            Post(
                body=f"{prefix} {index + 1}",
                author=author,
                created_at=start + timedelta(minutes=index),
            )
        )


def test_authenticated_user_can_create_post(client, app):
    with app.app_context():
        user = User(username="alice", email="alice@example.com")
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
        alice = User(username="alice", email="alice@example.com")
        alice.set_password("study123")
        bob = User(username="bob", email="bob@example.com")
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


def test_authenticated_home_is_paginated(client, app):
    with app.app_context():
        alice = User(username="alice", email="alice@example.com")
        alice.set_password("study123")
        bob = User(username="bob", email="bob@example.com")
        bob.set_password("study123")
        db.session.add_all([alice, bob])
        db.session.commit()

        alice.follow(bob)
        add_posts(bob, "home note", 6)
        db.session.commit()

    login(client, "alice", "study123")

    page1 = client.get("/", follow_redirects=True).get_data(as_text=True)
    page2 = client.get("/?page=2", follow_redirects=True).get_data(as_text=True)

    assert "home note 6" in page1
    assert "home note 2" in page1
    assert "home note 1" not in page1
    assert "Страница 1 из 2" in page1
    assert "home note 1" in page2
    assert "home note 6" not in page2
    assert "Страница 2 из 2" in page2


def test_public_feed_is_paginated(client, app):
    with app.app_context():
        alice = User(username="alice", email="alice@example.com")
        alice.set_password("study123")
        db.session.add(alice)
        db.session.commit()

        add_posts(alice, "feed note", 6)
        db.session.commit()

    page1 = client.get("/feed").get_data(as_text=True)
    page2 = client.get("/feed?page=2").get_data(as_text=True)

    assert "feed note 6" in page1
    assert "feed note 1" not in page1
    assert "Страница 1 из 2" in page1
    assert "feed note 1" in page2
    assert "feed note 6" not in page2


def test_user_profile_is_paginated(client, app):
    with app.app_context():
        alice = User(username="alice", email="alice@example.com")
        alice.set_password("study123")
        db.session.add(alice)
        db.session.commit()

        add_posts(alice, "profile note", 6)
        db.session.commit()

    page1 = client.get("/user/alice").get_data(as_text=True)
    page2 = client.get("/user/alice?page=2").get_data(as_text=True)

    assert "profile note 6" in page1
    assert "profile note 1" not in page1
    assert "Страница 1 из 2" in page1
    assert "profile note 1" in page2
    assert "profile note 6" not in page2
