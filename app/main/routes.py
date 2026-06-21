from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.main import bp
from app.main.forms import EditProfileForm, EmptyForm, PostForm
from app.models import Post, User


@bp.route("/", methods=["GET", "POST"])
def home():
    if current_user.is_authenticated:
        form = PostForm()
        if form.validate_on_submit():
            post = Post(body=form.body.data.strip(), author=current_user)
            db.session.add(post)
            db.session.commit()
            flash("Заметка опубликована.", "success")
            return redirect(url_for("main.home"))

        posts = current_user.followed_posts().all()
        return render_template(
            "main/index.html",
            title="My feed",
            form=form,
            posts=posts,
        )

    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()
    return render_template(
        "main/index.html",
        title="StudyLog",
        recent_posts=recent_posts,
    )


@bp.route("/feed")
def feed():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("main/feed.html", title="Feed", posts=posts)


@bp.route("/user/<username>")
def user(username: str):
    profile = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    posts = profile.posts.order_by(Post.created_at.desc()).all()
    return render_template(
        "main/user.html",
        title=profile.username,
        profile=profile,
        posts=posts,
        form=form,
    )


@bp.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data.strip()
        current_user.about_me = form.about_me.data.strip()
        db.session.commit()
        flash("Профиль обновлен.", "success")
        return redirect(url_for("main.user", username=current_user.username))

    if not form.is_submitted():
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template("main/edit_profile.html", title="Edit profile", form=form)


@bp.route("/follow/<username>", methods=["POST"])
@login_required
def follow(username: str):
    form = EmptyForm()
    if not form.validate_on_submit():
        abort(400)

    user_to_follow = User.query.filter_by(username=username).first_or_404()
    if user_to_follow == current_user:
        flash("Нельзя подписаться на самого себя.", "warning")
        return redirect(url_for("main.user", username=username))

    current_user.follow(user_to_follow)
    db.session.commit()
    flash(f"Вы подписались на {username}.", "success")
    return redirect(url_for("main.user", username=username))


@bp.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow(username: str):
    form = EmptyForm()
    if not form.validate_on_submit():
        abort(400)

    user_to_unfollow = User.query.filter_by(username=username).first_or_404()
    if user_to_unfollow == current_user:
        flash("Нельзя отписаться от самого себя.", "warning")
        return redirect(url_for("main.user", username=username))

    current_user.unfollow(user_to_unfollow)
    db.session.commit()
    flash(f"Вы отписались от {username}.", "success")
    return redirect(url_for("main.user", username=username))
