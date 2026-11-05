from fastapi import HTTPException, status
from typing import Callable, Any
from functools import wraps


class MurmurConnectionError(HTTPException):
    def __init__(self, detail: str = "Murmur Ice service is unreachable or timed out"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


class MurmurAuthenticationError(HTTPException):
    def __init__(self, detail: str = "Invalid Murmur administrative secret"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class MurmurServerBootError(HTTPException):
    def __init__(self, detail: str = "Murmur failed to boot virtual server"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class MurmurRPCError(HTTPException):
    def __init__(self, detail: str = "Murmur RPC operation failed"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)


def handle_ice_errors(func: Callable) -> Callable:
    """
    Decorator to wrap route handlers and translate ZeroC Ice / Murmur exceptions
    into structured FastAPI HTTPExceptions.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as e:
            err_type = type(e).__name__
            err_msg = str(e)
            combined_err = f"{err_type} {err_msg}"

            # Match common ZeroC Ice exception class names and messages
            if "ConnectionRefused" in combined_err or "SocketException" in combined_err or "ConnectFailedException" in combined_err:
                raise MurmurConnectionError(f"Cannot connect to Murmur Ice at server endpoint: {err_msg}")
            elif "TimeoutException" in combined_err:
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail=f"Murmur Ice request timed out: {err_msg}"
                )
            elif "InvalidSecret" in combined_err:
                raise MurmurAuthenticationError(f"Murmur secret rejected: {err_msg}")
            elif "ServerBootFailed" in combined_err:
                raise MurmurServerBootError(f"Murmur virtual server boot failed: {err_msg}")
            elif "CommunicatorDestroyed" in combined_err:
                raise MurmurConnectionError("Ice communicator is shut down or destroyed.")
            else:
                # Fallback for other unexpected Murmur/Ice RPC errors
                raise MurmurRPCError(f"Murmur RPC error ({err_type}): {err_msg}")
    return wrapper
