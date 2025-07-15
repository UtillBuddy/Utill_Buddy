import pytest
from unittest.mock import patch
from firebase_admin import credentials

@pytest.fixture(autouse=True)
def mock_firebase_admin():
    class MockCertificate(credentials.Base):
        def __init__(self):
            pass

        def get_access_token(self):
            pass

    with patch("firebase_admin.credentials.Certificate", return_value=MockCertificate()) as mock_certificate, \
         patch("firebase_admin.initialize_app") as mock_initialize_app, \
         patch("firebase_admin.auth") as mock_auth, \
         patch("firebase_admin.storage") as mock_storage:
        yield mock_certificate, mock_initialize_app, mock_auth, mock_storage
