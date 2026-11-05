import pytest
from starlette.testclient import TestClient
from main import mumble_rest
from app.ice_manager import ice_manager
from tests.mock_ice import MockMeta
import settings


@pytest.fixture(autouse=True)
def setup_mock_ice():
    """
    Automatically injects a fresh MockMeta into ice_manager before every test.
    Restores ice_manager state afterwards.
    """
    mock_meta = MockMeta()
    ice_manager.set_meta(mock_meta)
    
    # Ensure default test settings
    original_api_key = settings.API_KEY
    original_mask = settings.MASK_PASSWORDS
    settings.API_KEY = ""
    settings.MASK_PASSWORDS = True

    yield mock_meta

    # Cleanup
    settings.API_KEY = original_api_key
    settings.MASK_PASSWORDS = original_mask
    ice_manager.close()


@pytest.fixture
def client():
    """
    Returns a Starlette TestClient configured for mumble_rest app.
    """
    with TestClient(mumble_rest, raise_server_exceptions=False) as test_client:
        yield test_client

