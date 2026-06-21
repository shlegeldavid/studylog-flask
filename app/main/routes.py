from flask import abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.main import bp
from app.main.forms import EditProfileForm, EmptyForm, PostForm
from app.models import Post, User


def get_page_number() -> int:
    page = request.args.get("page", 1, type=int)
    if page is None or page < 1:
        return 1
    return page


def build_page_urls(endpoint: str, pagination, **values: object) -> tuple[str | None, str | None]:
    prev_url = (
        url_for(endpoint, page=pagination.prev_num, **values)
        if pagination.has_prev
        else None
    )
    next_url = (
        url_for(endpoint, page=pagination.next_num, **values)
        if pagination.has_next
        else None
    )
    return prev_url, next_url


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

        page = get_page_number()
        pagination = current_user.followed_posts().paginate(
            page=page,
            per_page=current_app.config["POSTS_PER_PAGE"],
            error_out=False,
        )
        posts = pagination.items
        prev_url, next_url = build_page_urls("main.home", pagination)
        return render_template(
            "main/index.html",
            title="Моя лента",
            form=form,
            posts=posts,
            pagination=pagination,
            prev_url=prev_url,
            next_url=next_url,
        )

    recent_posts = (
        Post.query.order_by(Post.created_at.desc())
        .limit(current_app.config["POSTS_PER_PAGE"])
        .all()
    )
    return render_template(
        "main/index.html",
        title="Главная",
        recent_posts=recent_posts,
    )


@bp.route("/feed")
def feed():
    page = get_page_number()
    pagination = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page,
        per_page=current_app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    posts = pagination.items
    prev_url, next_url = build_page_urls("main.feed", pagination)
    return render_template(
        "main/feed.html",
        title="Общая лента",
        posts=posts,
        pagination=pagination,
        prev_url=prev_url,
        next_url=next_url,
    )


@bp.route("/user/<username>")
def user(username: str):
    profile = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    page = get_page_number()
    pagination = profile.posts.order_by(Post.created_at.desc()).paginate(
        page=page,
        per_page=current_app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    posts = pagination.items
    prev_url, next_url = build_page_urls("main.user", pagination, username=username)
    return render_template(
        "main/user.html",
        title=f"Профиль {profile.username}",
        profile=profile,
        posts=posts,
        form=form,
        pagination=pagination,
        prev_url=prev_url,
        next_url=next_url,
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

    return render_template(
        "main/edit_profile.html",
        title="Редактирование профиля",
        form=form,
    )


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
