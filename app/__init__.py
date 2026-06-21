from __future__ import annotations

import click
from flask import Flask, render_template

from app.extensions import db, login_manager, migrate
from config import Config


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.auth import bp as auth_bp
    from app.main import bp as main_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)

    from app.models import Post, User

    @app.shell_context_processor
    def make_shell_context() -> dict[str, object]:
        return {"db": db, "User": User, "Post": Post}

    @app.get("/health")
    def healthcheck() -> tuple[str, int]:
        return "ok", 200

    @app.cli.command("init-db")
    def init_db_command() -> None:
        db.create_all()
        click.echo("Database tables created.")

    @app.cli.command("seed-demo")
    def seed_demo_command() -> None:
        demo_users = [
            {"username": "demo", "email": "demo@example.com", "password": "demo123"},
            {"username": "alice", "email": "alice@example.com", "password": "demo123"},
            {"username": "bob", "email": "bob@example.com", "password": "demo123"},
        ]
        users: dict[str, User] = {}

        for data in demo_users:
            user = User.query.filter_by(username=data["username"]).first()
            if user is None:
                user = User(username=data["username"], email=data["email"])
                db.session.add(user)
            else:
                user.email = data["email"]

            user.set_password(data["password"])
            users[user.username] = user

        db.session.flush()

        demo_posts = [
            ("demo", "Сегодня повторил основы Flask и работу с blueprints."),
            ("demo", "Разобрался, как работает Flask-Login в учебном проекте."),
            ("alice", "Сделала краткий конспект по SQLAlchemy и моделям."),
            ("alice", "Добавила шаблоны Jinja2 и проверила маршруты."),
            ("bob", "Повторил формы Flask-WTF и базовую валидацию."),
            ("bob", "Подготовил тестовые заметки для общей ленты."),
        ]

        for username, body in demo_posts:
            author = users[username]
            post = Post.query.filter_by(user_id=author.id, body=body).first()
            if post is None:
                db.session.add(Post(body=body, author=author))

        if not users["demo"].is_following(users["alice"]):
            users["demo"].follow(users["alice"])

        db.session.commit()
        click.echo("Демо-данные созданы или обновлены.")

    @app.errorhandler(404)
    def not_found_error(error: Exception):
        return render_template("errors/404.html", title="Страница не найдена"), 404

    @app.errorhandler(500)
    def internal_error(error: Exception):
        db.session.rollback()
        return render_template("errors/500.html", title="Ошибка сервера"), 500

    return app
