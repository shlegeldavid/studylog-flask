from datetime import UTC, datetime, timedelta

from app.extensions import db
from app.models import Post, User


def test_user_can_follow_and_unfollow(app):
    with app.app_context():
        alice = User(username="alice", email="alice@example.com")
        alice.set_password("study123")
        bob = User(username="bob", email="bob@example.com")
        bob.set_password("study123")
        db.session.add_all([alice, bob])
        db.session.commit()

        assert not alice.is_following(bob)
        alice.follow(bob)
        db.session.commit()

        assert alice.is_following(bob)
        assert bob.followers.count() == 1

        alice.unfollow(bob)
        db.session.commit()

        assert not alice.is_following(bob)


def test_followed_posts_include_own_and_followed_posts(app):
    with app.app_context():
        alice = User(username="alice", email="alice@example.com")
        alice.set_password("study123")
        bob = User(username="bob", email="bob@example.com")
        bob.set_password("study123")
        carol = User(username="carol", email="carol@example.com")
        carol.set_password("study123")
        db.session.add_all([alice, bob, carol])
        db.session.commit()

        now = datetime.now(UTC).replace(tzinfo=None)
        db.session.add_all(
            [
                Post(body="my post", author=alice, created_at=now - timedelta(minutes=2)),
                Post(body="followed post", author=bob, created_at=now - timedelta(minutes=1)),
                Post(body="hidden post", author=carol, created_at=now),
            ]
        )
        alice.follow(bob)
        db.session.commit()

        bodies = [post.body for post in alice.followed_posts().all()]

        assert bodies == ["followed post", "my post"]
