from fastapi.testclient import TestClient
from backend.main import create_app


def test_read_root():
    app = create_app()
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 404
