import json
import os
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from src import app as app_module


def test_login_and_signup_require_teacher_auth(monkeypatch):
    credentials = {
        "teachers": [
            {"username": "teacher", "password": "password123"}
        ]
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        cred_path = Path(tmpdir) / "admin_credentials.json"
        cred_path.write_text(json.dumps(credentials), encoding="utf-8")
        monkeypatch.setenv("ADMIN_CREDENTIALS_FILE", str(cred_path))
        import importlib

        importlib.reload(app_module)
        client = TestClient(app_module.app)

        unauthenticated = client.post(
            "/activities/Chess Club/signup",
            params={"email": "student@example.edu"},
        )
        assert unauthenticated.status_code == 403

        login_response = client.post(
            "/auth/login",
            json={"username": "teacher", "password": "password123"},
        )
        assert login_response.status_code == 200

        signed_up = client.post(
            "/activities/Chess Club/signup",
            params={"email": "student@example.edu"},
        )
        assert signed_up.status_code == 200
