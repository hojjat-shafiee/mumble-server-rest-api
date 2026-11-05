from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Any, Optional
from datetime import timedelta
import settings
from app.ice_manager import get_ice_meta
from app.models import ServerModel, ServerUpdateModel
from app.utils import get_server_conf, get_server_port, obj_to_dict
from app.security import verify_api_key
from app.exceptions import handle_ice_errors

router = APIRouter(tags=["Servers"])


def _build_server_detail_dict(meta: Any, server: Any) -> dict[str, Any]:
    """Helper to build serialized server detail dictionary."""
    is_running = server.isRunning()
    tree = obj_to_dict(server.getTree()) if is_running else None
    
    raw_password = get_server_conf(meta, server, "password")
    if settings.MASK_PASSWORDS and raw_password:
        password_value = "***"
    else:
        password_value = raw_password

    uptime = server.getUptime() if is_running else 0
    return {
        "id": server.id(),
        "name": get_server_conf(meta, server, "registername"),
        "host": get_server_conf(meta, server, "host"),
        "port": get_server_port(meta, server),
        "address": "%s:%s" % (
            get_server_conf(meta, server, "host"),
            get_server_port(meta, server),
        ),
        "password": password_value,
        "welcometext": get_server_conf(meta, server, "welcometext"),
        "user_count": (is_running and len(server.getUsers())) or 0,
        "maxusers": get_server_conf(meta, server, "users") or 0,
        "running": is_running,
        "uptime": uptime,
        "humanize_uptime": str(timedelta(seconds=uptime) if is_running else ""),
        "parent_channel": tree["c"] if tree and "c" in tree else None,
        "sub_channels": tree["children"] if tree and "children" in tree else None,
        "users": tree["users"] if tree and "users" in tree else None,
        "registered_users": (
            server.getRegisteredUsers("") if is_running and hasattr(server, "getRegisteredUsers") else None
        ),
        "log_length": server.getLogLen(),
    }


# ---------------------------------------------------------------------------
# Version & Metadata
# ---------------------------------------------------------------------------

@router.get("/murmur-version", summary="Get Murmur Version")
@handle_ice_errors
def murmur_version(meta: Any = Depends(get_ice_meta)):
    """Returns the underlying Murmur Ice version."""
    version = meta.getVersion()
    return {"version": f"{version}"}


# ---------------------------------------------------------------------------
# Server Listing & Details
# ---------------------------------------------------------------------------

@router.get("", summary="List all servers")
@router.get("/getAllServers", summary="List all servers (Legacy alias)", include_in_schema=False)
@handle_ice_errors
def list_servers(meta: Any = Depends(get_ice_meta)):
    """
    Lists all virtual servers hosted by Murmur along with runtime statistics.
    Uses synchronous execution in FastAPI worker threadpool to prevent event loop blocking.
    """
    servers = []
    for s in meta.getAllServers():
        host = get_server_conf(meta, s, "host")
        port = get_server_port(meta, s)
        is_running = s.isRunning()
        uptime = s.getUptime() if is_running else 0

        servers.append(
            {
                "id": s.id(),
                "name": get_server_conf(meta, s, "registername"),
                "address": "%s:%s" % (host, port),
                "host": host,
                "port": port,
                "running": is_running,
                "users": (is_running and len(s.getUsers())) or 0,
                "maxusers": get_server_conf(meta, s, "users") or 0,
                "channels": (is_running and len(s.getChannels())) or 0,
                "uptime_seconds": uptime if is_running else 0,
                "uptime": str(timedelta(seconds=uptime) if is_running else ""),
                "log_length": s.getLogLen(),
            }
        )
    return servers


@router.get("/getServerDetail", summary="Get server detail (Legacy query alias)", include_in_schema=False)
@handle_ice_errors
def get_server_detail_legacy(id: int = Query(..., description="Server ID"), meta: Any = Depends(get_ice_meta)):
    """Legacy alias retrieving server details using a query parameter (?id=X)."""
    return get_server_detail(id=id, meta=meta)


@router.get("/{id}", summary="Get server detail")
@handle_ice_errors
def get_server_detail(id: int, meta: Any = Depends(get_ice_meta)):
    """
    Returns full details for a virtual server including channels, active users, and configuration.
    """
    server = meta.getServer(id)
    if server is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Server with id {id} not found")
    return _build_server_detail_dict(meta, server)


# ---------------------------------------------------------------------------
# Server Lifecycle Management
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a new server")
@router.post("/createServer", status_code=status.HTTP_201_CREATED, summary="Create a server (Legacy alias)", include_in_schema=False)
@handle_ice_errors
def create_server(
    model: ServerModel,
    meta: Any = Depends(get_ice_meta),
    _auth: bool = Depends(verify_api_key),
):
    """
    Creates a new virtual server, applies configuration options, boots it up, and returns server details.
    """
    server = meta.newServer()
    if model.password is not None:
        server.setConf("password", model.password)
    if model.port is not None:
        server.setConf("port", str(model.port))
    if model.timeout is not None:
        server.setConf("timeout", str(model.timeout))
    if model.bandwidth is not None:
        server.setConf("bandwidth", str(model.bandwidth))
    if model.users is not None:
        server.setConf("users", str(model.users))
    if model.welcomeText is not None:
        server.setConf("welcometext", model.welcomeText)
    if model.registerName is not None:
        server.setConf("registername", model.registerName)

    server.start()
    return _build_server_detail_dict(meta, server)


@router.patch("/{id}", summary="Update server configuration")
@handle_ice_errors
def update_server_config(
    id: int,
    model: ServerUpdateModel,
    meta: Any = Depends(get_ice_meta),
    _auth: bool = Depends(verify_api_key),
):
    """
    Updates the configuration of an existing virtual server.
    """
    server = meta.getServer(id)
    if server is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Server with id {id} not found")

    if model.password is not None:
        server.setConf("password", model.password)
    if model.timeout is not None:
        server.setConf("timeout", str(model.timeout))
    if model.bandwidth is not None:
        server.setConf("bandwidth", str(model.bandwidth))
    if model.users is not None:
        server.setConf("users", str(model.users))
    if model.welcomeText is not None:
        server.setConf("welcometext", model.welcomeText)
    if model.registerName is not None:
        server.setConf("registername", model.registerName)

    return {"message": f"Server {id} configuration updated successfully"}


@router.delete("/deleteAllServers", summary="Delete all servers (Legacy alias)", include_in_schema=False)
@router.delete("/all", summary="Delete all servers")
@handle_ice_errors
def delete_all_servers(
    meta: Any = Depends(get_ice_meta),
    _auth: bool = Depends(verify_api_key),
):
    """
    Stops and deletes all virtual servers on this Murmur instance.
    """
    deleted_servers: list[int] = []
    for s in meta.getAllServers():
        try:
            s_id = s.id()
            if s.isRunning():
                s.stop()
            s.delete()
            deleted_servers.append(s_id)
        except Exception:
            continue
    return {"deleted_servers": deleted_servers}


@router.delete("/deleteServers", summary="Batch delete servers (Legacy alias)", include_in_schema=False)
@router.post("/batch-delete", summary="Batch delete servers")
@handle_ice_errors
def batch_delete_servers(
    id_list: list[int],
    meta: Any = Depends(get_ice_meta),
    _auth: bool = Depends(verify_api_key),
):
    """
    Stops and deletes multiple virtual servers by ID list.
    """
    deleted_servers: list[int] = []
    for s_id in id_list:
        server = meta.getServer(s_id)
        if not server:
            continue
        try:
            if server.isRunning():
                server.stop()
            server.delete()
            deleted_servers.append(s_id)
        except Exception:
            continue
    return {"deleted_servers": deleted_servers}


@router.delete("/deleteServer", summary="Delete a server (Legacy query alias)", include_in_schema=False)
@handle_ice_errors
def delete_server_legacy(
    id: int = Query(..., description="Server ID"),
    meta: Any = Depends(get_ice_meta),
    _auth: bool = Depends(verify_api_key),
):
    """Legacy alias deleting a virtual server using query parameter (?id=X)."""
    return delete_server(id=id, meta=meta, _auth=_auth)


@router.delete("/{id}", summary="Delete a server")
@handle_ice_errors
def delete_server(
    id: int,
    meta: Any = Depends(get_ice_meta),
    _auth: bool = Depends(verify_api_key),
):
    """
    Shuts down and deletes a virtual server instance.
    """
    server = meta.getServer(id)
    if server is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Server with id {id} not found")

    if server.isRunning():
        server.stop()

    server.delete()
    return {"detail": f"server with id {id} deleted successfully"}


@router.post("/{id}/start", summary="Start a server")
@handle_ice_errors
def start(
    id: int,
    meta: Any = Depends(get_ice_meta),
    _auth: bool = Depends(verify_api_key),
):
    """Starts an inactive virtual server."""
    server = meta.getServer(id)
    if server is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Server with id {id} not found")

    if server.isRunning():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Server already running.")
    server.start()
    return {"message": f"server {id} started"}


@router.post("/{id}/stop", summary="Stop a server")
@handle_ice_errors
def stop(
    id: int,
    meta: Any = Depends(get_ice_meta),
    _auth: bool = Depends(verify_api_key),
):
    """Stops an active virtual server."""
    server = meta.getServer(id)
    if server is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Server with id {id} not found")

    if not server.isRunning():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Server already stopped.")
    server.stop()
    return {"message": f"server {id} stopped"}


@router.post("/{id}/restart", summary="Restart a server")
@handle_ice_errors
def restart(
    id: int,
    meta: Any = Depends(get_ice_meta),
    _auth: bool = Depends(verify_api_key),
):
    """Restarts a virtual server (stops if running, then starts)."""
    server = meta.getServer(id)
    if server is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Server with id {id} not found")

    if server.isRunning():
        server.stop()
    server.start()
    return {"message": f"server {id} restarted"}


# ---------------------------------------------------------------------------
# Server Logs
# ---------------------------------------------------------------------------

@router.get("/{id}/logs", summary="Get server logs")
@handle_ice_errors
def get_logs(
    id: int,
    first: int = Query(0, ge=0, description="First log index"),
    last: int = Query(-1, description="Last log index (-1 for latest)"),
    meta: Any = Depends(get_ice_meta),
):
    """Gets sorted server logs for the given server ID."""
    server = meta.getServer(id)
    if server is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Server with id {id} not found")

    logs = []
    log_entries = server.getLog(first, last) or []
    for log in log_entries:
        logs.append(
            {
                "message": getattr(log, "txt", str(log)),
                "timestamp": getattr(log, "timestamp", 0),
            }
        )
    logs.sort(key=lambda item: item["timestamp"])
    return logs
