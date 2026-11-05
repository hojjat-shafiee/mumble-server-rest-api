from typing import Any, Optional


class MockLog:
    def __init__(self, txt: str, timestamp: int):
        self.txt = txt
        self.timestamp = timestamp


class MockServer:
    def __init__(
        self,
        server_id: int = 1,
        running: bool = True,
        conf: Optional[dict[str, str]] = None,
    ):
        self._id = server_id
        self._running = running
        self._deleted = False
        self._conf = conf or {
            "registername": f"Mock Server {server_id}",
            "host": "127.0.0.1",
            "port": str(64738 + server_id - 1),
            "password": "secret_password_123",
            "welcometext": "Welcome to Murmur",
            "users": "100",
        }
        self._users = [{"name": "alice", "session": 1}] if running else []
        self._channels = [{"id": 0, "name": "Root"}] if running else []
        self._logs = [
            MockLog("Server booted", 1000),
            MockLog("User connected", 2000),
        ]

    def id(self) -> int:
        return self._id

    def isRunning(self) -> bool:
        return self._running

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def delete(self) -> None:
        self._deleted = True

    def getConf(self, key: str) -> str:
        return self._conf.get(key, "")

    def setConf(self, key: str, val: Any) -> None:
        self._conf[key] = str(val)

    def getUsers(self) -> list[dict[str, Any]]:
        return self._users

    def getChannels(self) -> list[dict[str, Any]]:
        return self._channels

    def getUptime(self) -> int:
        return 3600 if self._running else 0

    def getLogLen(self) -> int:
        return len(self._logs)

    def getLog(self, first: int, last: int) -> list[MockLog]:
        return self._logs

    def getTree(self) -> dict[str, Any]:
        return {
            "c": {"id": 0, "name": "Root"},
            "children": [],
            "users": self._users,
        }

    def getRegisteredUsers(self, filter_name: str) -> list[dict[str, Any]]:
        return [{"id": 1, "name": "SuperUser"}]


class MockMeta:
    def __init__(self):
        self._servers: dict[int, MockServer] = {
            1: MockServer(1, running=True),
            2: MockServer(2, running=False),
        }
        self._next_id = 3
        self._version = "1.4.0"
        self._default_conf = {
            "port": "64738",
            "timeout": "30",
            "bandwidth": "72000",
            "users": "100",
        }

    def getVersion(self) -> str:
        return self._version

    def getDefaultConf(self) -> dict[str, str]:
        return self._default_conf

    def getAllServers(self) -> list[MockServer]:
        return [s for s in self._servers.values() if not s._deleted]

    def getServer(self, server_id: int) -> Optional[MockServer]:
        s = self._servers.get(server_id)
        if s and not s._deleted:
            return s
        return None

    def newServer(self) -> MockServer:
        new_id = self._next_id
        self._next_id += 1
        server = MockServer(new_id, running=False)
        self._servers[new_id] = server
        return server

