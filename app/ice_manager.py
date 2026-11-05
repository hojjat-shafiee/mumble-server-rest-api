import logging
from typing import Any, Optional
import settings
from app.exceptions import MurmurConnectionError, MurmurAuthenticationError

logger = logging.getLogger("mumble_rest.ice")

class IceManager:
    """
    Manages the ZeroC Ice Communicator lifecycle and Murmur Meta proxy.
    Provides lazy connection, health check probing, graceful teardown,
    and mock injection for test harnesses.
    """
    def __init__(self):
        self._communicator: Any = None
        self._meta: Any = None
        self._is_mock: bool = False

    def is_available(self) -> bool:
        """Checks if the Ice module is importable in the runtime environment."""
        try:
            import Ice  # noqa: F401
            import Murmur  # noqa: F401
            return True
        except ImportError:
            return False

    def connect(self) -> Any:
        """
        Initializes the Ice Communicator and casts the proxy to Murmur.MetaPrx.
        Returns the Meta proxy instance.
        """
        if self._meta is not None:
            return self._meta

        try:
            import Ice
            import Murmur
        except ImportError as e:
            logger.error("ZeroC Ice or Murmur Python bindings are not installed: %s", e)
            raise MurmurConnectionError(
                "ZeroC Ice is not installed in this environment. Run inside the Debian container or supply a mock."
            )

        try:
            props = Ice.createProperties()
            props.setProperty("Ice.ImplicitContext", "Shared")
            props.setProperty("Ice.Default.EncodingVersion", "1.0")
            props.setProperty("Ice.Default.InvocationTimeout", str(settings.ICE_TIMEOUT))
            props.setProperty("Ice.MessageSizeMax", str(settings.ICE_MESSAGE_SIZE))

            init_data = Ice.InitializationData()
            init_data.properties = props

            self._communicator = Ice.initialize(init_data)
            proxy = self._communicator.stringToProxy(settings.ICE_HOST)

            if settings.ICE_SECRET:
                self._communicator.getImplicitContext().put("secret", settings.ICE_SECRET)

            meta = Murmur.MetaPrx.checkedCast(proxy)
            if not meta:
                raise MurmurConnectionError(f"Failed to cast proxy to Murmur.MetaPrx at {settings.ICE_HOST}")

            self._meta = meta
            logger.info("Successfully connected to Murmur Ice at %s", settings.ICE_HOST)
            return self._meta
        except Exception as e:
            self.close()
            err_name = type(e).__name__
            if "InvalidSecret" in err_name:
                raise MurmurAuthenticationError(f"Murmur rejected secret: {e}")
            raise MurmurConnectionError(f"Failed to connect to Murmur Ice: {e}")

    def get_meta(self) -> Any:
        """
        Retrieves the active Murmur Meta proxy, attempting connection if not yet connected.
        """
        if self._meta is not None:
            return self._meta
        return self.connect()

    def set_meta(self, mock_meta: Any) -> None:
        """
        Injects a mock Meta proxy for unit and integration testing harnesses.
        """
        self._meta = mock_meta
        self._is_mock = True

    def check_health(self) -> dict[str, Any]:
        """
        Probes the Murmur Ice connection and returns health status metadata.
        """
        if self._meta is None and not self._is_mock:
            try:
                self.connect()
            except Exception as e:
                return {"status": "unhealthy", "connected": False, "error": str(e)}

        try:
            if hasattr(self._meta, "getVersion"):
                version = self._meta.getVersion()
                return {"status": "healthy", "connected": True, "murmur_version": str(version)}
            return {"status": "healthy", "connected": True}
        except Exception as e:
            return {"status": "unhealthy", "connected": False, "error": str(e)}

    def close(self) -> None:
        """
        Gracefully destroys the Ice Communicator and releases network sockets.
        """
        if self._communicator is not None:
            try:
                self._communicator.destroy()
            except Exception as e:
                logger.warning("Error destroying Ice communicator: %s", e)
            finally:
                self._communicator = None
        if not self._is_mock:
            self._meta = None


# Global singleton instance
ice_manager = IceManager()


def get_ice_meta() -> Any:
    """
    FastAPI dependency provider to inject the Murmur Meta proxy into route handlers.
    """
    return ice_manager.get_meta()

