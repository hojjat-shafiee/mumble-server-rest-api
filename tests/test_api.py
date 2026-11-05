import pytest
from fastapi import status
import settings
from app.exceptions import MurmurConnectionError


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["service"] == "mumble-server-rest-api"
    assert "version" in data


def test_healthz_endpoint(client):
    response = client.get("/healthz")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["connected"] is True
    assert data["murmur_version"] == "1.4.0"


def test_list_servers(client):
    # Modern REST route
    response = client.get("/servers")
    assert response.status_code == status.HTTP_200_OK
    servers = response.json()
    assert len(servers) == 2
    assert servers[0]["id"] == 1
    assert servers[0]["running"] is True
    assert servers[1]["id"] == 2
    assert servers[1]["running"] is False

    # Legacy alias route
    legacy_response = client.get("/server/getAllServers")
    assert legacy_response.status_code == status.HTTP_200_OK
    assert legacy_response.json() == servers


def test_get_server_detail(client):
    # Modern REST route
    response = client.get("/servers/1")
    assert response.status_code == status.HTTP_200_OK
    detail = response.json()
    assert detail["id"] == 1
    assert detail["running"] is True
    assert detail["user_count"] == 1
    # Check password masking
    assert detail["password"] == "***"

    # Legacy query param alias route
    legacy_response = client.get("/server/getServerDetail?id=1")
    assert legacy_response.status_code == status.HTTP_200_OK
    assert legacy_response.json()["id"] == 1


def test_get_server_detail_unmasked_password(client):
    settings.MASK_PASSWORDS = False
    response = client.get("/servers/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["password"] == "secret_password_123"


def test_get_server_detail_not_found(client):
    response = client.get("/servers/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_server(client):
    payload = {
        "registerName": "New Test Server",
        "port": 65000,
        "users": 50,
        "welcomeText": "Hello World",
        "password": "testpassword",
    }
    response = client.post("/servers", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "New Test Server"
    assert data["port"] == 65000
    assert data["running"] is True


def test_update_server_config(client):
    payload = {
        "registerName": "Renamed Server",
        "users": 200,
    }
    response = client.patch("/servers/1", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert "updated successfully" in response.json()["message"]

    detail = client.get("/servers/1").json()
    assert detail["name"] == "Renamed Server"


def test_start_and_stop_server(client):
    # Server 2 is initially stopped
    start_resp = client.post("/servers/2/start")
    assert start_resp.status_code == status.HTTP_200_OK
    assert start_resp.json()["message"] == "server 2 started"

    # Starting already running server should fail with 400
    dup_start = client.post("/servers/2/start")
    assert dup_start.status_code == status.HTTP_400_BAD_REQUEST

    # Stop server 2
    stop_resp = client.post("/servers/2/stop")
    assert stop_resp.status_code == status.HTTP_200_OK
    assert stop_resp.json()["message"] == "server 2 stopped"

    # Stopping already stopped server should fail with 400
    dup_stop = client.post("/servers/2/stop")
    assert dup_stop.status_code == status.HTTP_400_BAD_REQUEST


def test_restart_server(client):
    restart_resp = client.post("/servers/1/restart")
    assert restart_resp.status_code == status.HTTP_200_OK
    assert restart_resp.json()["message"] == "server 1 restarted"


def test_delete_server(client):
    del_resp = client.delete("/servers/2")
    assert del_resp.status_code == status.HTTP_200_OK
    assert "deleted successfully" in del_resp.json()["detail"]

    # Verify not found afterwards
    get_resp = client.get("/servers/2")
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND


def test_batch_delete_servers(client):
    resp = client.post("/servers/batch-delete", json=[1, 2])
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["deleted_servers"] == [1, 2]


def test_server_logs(client):
    resp = client.get("/servers/1/logs")
    assert resp.status_code == status.HTTP_200_OK
    logs = resp.json()
    assert len(logs) == 2
    assert logs[0]["message"] == "Server booted"
    assert logs[1]["message"] == "User connected"


def test_api_key_authentication(client):
    settings.API_KEY = "my_super_secret_key"

    # Request without API Key should return 401
    unauth_resp = client.post("/servers/1/start")
    assert unauth_resp.status_code == status.HTTP_401_UNAUTHORIZED

    # Request with X-API-Key header should succeed
    auth_resp = client.post("/servers/1/restart", headers={"X-API-Key": "my_super_secret_key"})
    assert auth_resp.status_code == status.HTTP_200_OK

    # Request with Bearer Token should succeed
    bearer_resp = client.post(
        "/servers/1/restart",
        headers={"Authorization": "Bearer my_super_secret_key"}
    )
    assert bearer_resp.status_code == status.HTTP_200_OK


def test_murmur_version_endpoint(client):
    resp = client.get("/servers/murmur-version")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["version"] == "1.4.0"


def test_legacy_delete_server_query_param(client):
    resp = client.delete("/server/deleteServer?id=2")
    assert resp.status_code == status.HTTP_200_OK
    assert "deleted successfully" in resp.json()["detail"]


def test_delete_all_servers(client):
    resp = client.delete("/servers/all")
    assert resp.status_code == status.HTTP_200_OK
    deleted = resp.json()["deleted_servers"]
    assert 1 in deleted or 2 in deleted


def test_ice_exception_handling(client, setup_mock_ice):
    # Simulate an Ice connection error during call
    class BrokenMeta:
        def getAllServers(self):
            raise Exception("Ice.ConnectionRefusedException: Connection refused")

    from app.ice_manager import ice_manager
    ice_manager.set_meta(BrokenMeta())

    resp = client.get("/servers")
    assert resp.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Cannot connect to Murmur Ice" in resp.json()["detail"]

