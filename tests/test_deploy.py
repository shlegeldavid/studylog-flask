from config import normalize_database_url
from wsgi import app as wsgi_app


def test_healthcheck_route_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "ok"


def test_normalize_database_url_supports_postgres_scheme():
    assert (
        normalize_database_url("postgres://user:pass@localhost:5432/studylog")
        == "postgresql://user:pass@localhost:5432/studylog"
    )


def test_wsgi_app_is_importable():
    assert wsgi_app is not None
