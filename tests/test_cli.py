from app.models import User


def test_seed_demo_creates_demo_user_without_duplicates(runner, app):
    first_run = runner.invoke(args=["seed-demo"])
    second_run = runner.invoke(args=["seed-demo"])

    assert first_run.exit_code == 0
    assert second_run.exit_code == 0
    assert "Демо-данные созданы" in first_run.output

    with app.app_context():
        users = User.query.filter_by(username="demo").all()

        assert len(users) == 1
        assert users[0].email == "demo@example.com"
        assert users[0].check_password("demo123")
