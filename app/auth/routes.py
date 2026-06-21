from urllib.parse import urlsplit

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.extensions import db
from app.models import User


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user is None or not user.check_password(form.password.data):
            flash("Неверное имя пользователя или пароль.", "error")
            return redirect(url_for("auth.login"))

        login_user(user, remember=form.remember_me.data)
        flash("Вы вошли в аккаунт.", "success")

        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc:
            next_page = url_for("main.home")
        return redirect(next_page)

    return render_template("auth/login.html", title="Login", form=form)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data.strip())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Аккаунт создан. Теперь можно войти.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", title="Register", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта.", "success")
    return redirect(url_for("main.home"))
