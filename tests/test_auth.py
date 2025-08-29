import os
import tempfile
import uuid
from fastapi.testclient import TestClient

# отдельный sqlite-файл на каждый прогон
db_dir = tempfile.mkdtemp()
db_path = os.path.join(db_dir, f"test_app_{uuid.uuid4().hex}.db")
os.environ["DB_URL"] = f"sqlite:///{db_path}"

from app.main import app  # noqa: E402

client = TestClient(app)

def test_register_login_flow():
    email = f"test_{uuid.uuid4().hex}@example.com"

    # register
    r = client.post("/register", json={"email": email, "password": "Secret123!"})
    assert r.status_code == 201, r.text
    assert r.json()["email"] == email

    # login
    r = client.post("/login", json={"email": email, "password": "Secret123!"})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]

    # public
    r = client.get("/public-data")
    assert r.status_code == 200

    # private
    r = client.get("/private-data", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert "Приватная" in r.json()["data"]
