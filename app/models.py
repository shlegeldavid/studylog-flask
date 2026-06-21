from __future__ import annotations

from datetime import UTC, datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager


followers = db.Table(
    "followers",
    db.Column("follower_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
)


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    about_me = db.Column(db.String(280), default="")
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    posts = db.relationship(
        "Post",
        back_populates="author",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    following = db.relationship(
        "User",
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref("followers", lazy="dynamic"),
        lazy="dynamic",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def follow(self, user: "User") -> None:
        if not self.is_following(user):
            self.following.append(user)

    def unfollow(self, user: "User") -> None:
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user: "User") -> bool:
        return (
            self.following.filter(followers.c.followed_id == user.id).first() is not None
        )

    def followed_posts(self):
        """Возвращает ленту из своих заметок и заметок тех, на кого подписан пользователь."""
        followed = Post.query.join(
            followers, followers.c.followed_id == Post.user_id
        ).filter(followers.c.follower_id == self.id)
        own_posts = Post.query.filter_by(user_id=self.id)
        return followed.union(own_posts).order_by(Post.created_at.desc())

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(280), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    author = db.relationship("User", back_populates="posts")

    def __repr__(self) -> str:
        return f"<Post {self.id}>"


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id))
