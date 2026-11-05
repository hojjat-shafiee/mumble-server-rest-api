from typing import Any
from collections.abc import Mapping, Sequence


def get_server_conf(meta: Any, server: Any, key: str) -> str:
    """
    Gets the server configuration for given server/key.
    Falls back to Murmur default configuration if server-level config is empty.
    """
    if server is None:
        return ""
    try:
        val = server.getConf(key)
        if val == "" and meta is not None:
            default_conf = meta.getDefaultConf()
            if isinstance(default_conf, dict):
                val = default_conf.get(key, "")
        return str(val) if val is not None else ""
    except Exception:
        return ""


def get_server_port(meta: Any, server: Any, val: Any = None) -> int:
    """
    Gets the server port value from configuration.
    Falls back to default base port + server ID offset if not explicitly set.
    """
    if server is None:
        return 0
    try:
        configured = server.getConf("port") if val is None else val
        if configured == "" or configured is None:
            default_port = 64738
            if meta is not None:
                default_conf = meta.getDefaultConf()
                if isinstance(default_conf, dict):
                    default_port = int(default_conf.get("port", 64738))
            server_id = server.id() if hasattr(server, "id") else 1
            return default_port + max(0, server_id - 1)
        return int(configured)
    except Exception:
        return 0


def get_all_users_count(meta: Any) -> int:
    """
    Gets the total number of connected users across all running servers.
    """
    if meta is None:
        return 0
    user_count = 0
    try:
        servers = meta.getAllServers() or []
        for s in servers:
            try:
                if s.isRunning():
                    users = s.getUsers()
                    user_count += len(users) if users else 0
            except Exception:
                continue
    except Exception:
        pass
    return user_count


def obj_to_dict(obj: Any) -> Any:
    """
    Safely converts objects returned from Murmur Ice RPC into JSON-serializable Python data structures.
    Handles None, primitive scalars, collections, mappings, __dict__, and __slots__ objects gracefully.
    """
    if obj is None:
        return None

    if isinstance(obj, (bool, int, float, str)):
        return obj

    if isinstance(obj, (bytes, bytearray)):
        try:
            return obj.decode("utf-8")
        except UnicodeDecodeError:
            return obj.hex()

    if isinstance(obj, (list, tuple, set)):
        return [obj_to_dict(item) for item in obj]

    if isinstance(obj, Mapping):
        return {str(k): obj_to_dict(v) for k, v in obj.items()}

    if hasattr(obj, "__dict__"):
        return obj_to_dict(obj.__dict__)

    if hasattr(obj, "__slots__"):
        slots_data = {}
        for slot in obj.__slots__:
            if hasattr(obj, slot):
                slots_data[slot] = obj_to_dict(getattr(obj, slot))
        return slots_data

    return str(obj)
