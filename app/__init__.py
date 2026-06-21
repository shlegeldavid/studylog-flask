from __future__ import annotations

import click
from flask import Flask

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

    @app.cli.command("init-db")
    def init_db_command() -> None:
        db.create_all()
        click.echo("Database tables created.")

    return app
