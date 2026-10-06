import secrets
from concurrent.futures import ThreadPoolExecutor

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text

from app.core.config import Settings
from app.main import create_app
from app.models.member import Member


@pytest.fixture
def configured_app(tmp_path):
    settings = Settings(
        _env_file=None,
        database_url=f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
        encryption_key=Fernet.generate_key().decode(),
        email_lookup_key=secrets.token_hex(32),
    )
    return create_app(settings), settings


@pytest.fixture
def client(configured_app):
    app, _ = configured_app
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def payload():
    return {
        "name": "테스트 회원",
        "email": "member@example.com",
        "password": "a long private passphrase!",
        "password_confirmation": "a long private passphrase!",
    }


def test_signup_encrypts_personal_data_and_hashes_password(client, payload):
    response = client.post("/api/auth/signup", json=payload)
    assert response.status_code == 201
    assert set(response.json()) == {"id", "created_at", "message"}
    assert response.headers["cache-control"] == "no-store"
    security = client.app.state.security
    with client.app.state.session_factory() as session:
        member = session.scalar(select(Member))
        assert member.id == response.json()["id"]
        assert security.decrypt(member.name_encrypted) == payload["name"]
        assert security.decrypt(member.email_encrypted) == payload["email"]
        assert member.email_lookup == security.email_index(payload["email"])
        assert member.password_hash.startswith("$argon2id$")
        assert security.password_hasher.verify(payload["password"], member.password_hash)
        stored_row = str(session.execute(text("SELECT * FROM members")).one())
        for key in ("name", "email", "password"):
            assert payload[key] not in stored_row
            assert payload[key] not in response.text


def test_duplicate_email_is_case_insensitive(client, payload):
    assert client.post("/api/auth/signup", json=payload).status_code == 201
    payload["email"] = " MEMBER@EXAMPLE.COM "
    duplicate = client.post("/api/auth/signup", json=payload)
    assert duplicate.status_code == 409
    assert "email" in duplicate.json()["errors"]
    with client.app.state.session_factory() as session:
        assert session.scalar(select(func.count()).select_from(Member)) == 1


@pytest.mark.parametrize("changes,field", [
    ({"email": "not-an-email"}, "email"),
    ({"name": " "}, "name"),
    ({"name": "a" * 51}, "name"),
    ({"name": "name\x00"}, "name"),
    ({"password": "short"}, "password"),
    ({"password": " " * 12, "password_confirmation": " " * 12}, "password"),
    ({"password": "x" * 129, "password_confirmation": "x" * 129}, "password"),
    ({"password_confirmation": "different password"}, "password_confirmation"),
])
def test_rejects_invalid_input_without_saving_or_echoing_secrets(client, payload, changes, field):
    payload.update(changes)
    response = client.post("/api/auth/signup", json=payload)
    assert response.status_code == 422
    assert field in response.json()["errors"]
    assert payload["password"] not in response.text
    with client.app.state.session_factory() as session:
        assert session.scalar(select(func.count()).select_from(Member)) == 0


def test_malformed_json_does_not_echo_request(client):
    response = client.post("/api/auth/signup", content='{"password":"secret', headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    assert "secret" not in response.text


def test_unexpected_field_is_rejected(client, payload):
    response = client.post("/api/auth/signup", json={**payload, "admin": True})
    assert response.status_code == 422


def test_concurrent_duplicate_requests_create_one_member(client, payload):
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: client.post("/api/auth/signup", json=payload).status_code, range(2)))
    assert sorted(results) == [201, 409]


def test_saved_member_survives_restart(configured_app, payload):
    app, settings = configured_app
    with TestClient(app) as first_client:
        response = first_client.post("/api/auth/signup", json=payload)
        assert response.status_code == 201
    second_app = create_app(settings)
    with TestClient(second_app) as second_client:
        assert second_client.post("/api/auth/signup", json=payload).status_code == 409
        with second_app.state.session_factory() as session:
            member = session.get(Member, response.json()["id"])
            assert second_app.state.security.decrypt(member.name_encrypted) == payload["name"]


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}
