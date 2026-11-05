# Architecture Deep-Dive — mumble-server-rest-api

This document provides architectural context for developers and AI agents working on `mumble-server-rest-api`.

---

## 1. System Overview

```
                      +---------------------------------------+
                      |               Clients                 |
                      |  (HTTP REST / Swagger / Third-Party)  |
                      +-------------------+-------------------+
                                          |
                                HTTP Port 2332
                                          v
                      +---------------------------------------+
                      |         FastAPI REST Layer            |
                      |  - Router & Endpoint Validation       |
                      |  - Pydantic v2 Models                 |
                      |  - Auth & Password Masking            |
                      |  - @handle_ice_errors Decorator       |
                      +-------------------+-------------------+
                                          |
                               Sync Threadpool Dispatch
                                          v
                      +---------------------------------------+
                      |          ZeroC Ice 3.7 RPC            |
                      |  - IceManager (Lifespan & Lazy Conn)  |
                      |  - Murmur.MetaPrx Proxy               |
                      |  - Murmur.ServerPrx Proxy             |
                      +-------------------+-------------------+
                                          |
                               TCP Socket Port 6502
                                          v
                      +---------------------------------------+
                      |        Murmur (Mumble Server)         |
                      |  - Virtual Server Manager             |
                      |  - Audio Channels & ACLs              |
                      +---------------------------------------+
```

---

## 2. ZeroC Ice RPC & Threading Model

### 2.1 Synchronous Socket RPC
ZeroC Ice Python bindings execute synchronous, blocking network calls over TCP sockets. 
- **The Pitfall**: Defining an endpoint as `async def` and calling `meta.getServer(id)` will block the central asyncio event loop, severely degrading API throughput.
- **The Solution**: All route handlers interacting with ZeroC Ice use standard `def`. FastAPI detects synchronous functions and automatically delegates their execution to Starlette's `run_in_threadpool`, ensuring the event loop remains responsive.

### 2.2 Ice Connection Lifecycle
- **Initialization**: Managed by `app.ice_manager.IceManager`.
- **Lifespan Hook**: In `main.py`, FastAPI's `lifespan` context manager calls `ice_manager.initialize()` on startup and `ice_manager.shutdown()` on shutdown.
- **Dependency Injection**: Route handlers never instantiate proxies directly; they receive `meta: Murmur.MetaPrx` via `Depends(get_ice_meta)`.

---

## 3. Slice Definitions & Generated Code
- `Murmur.ice`: ZeroC Slice IDL describing Murmur data structures and interfaces (`Meta`, `Server`, `Channel`, `User`).
- `Murmur_ice.py`: Generated Python wrapper produced by `slice2py`. 
  - **Constraint**: Never edit `Murmur_ice.py` directly. Any modifications will be overwritten if Slice definitions are recompiled.

---

## 4. Error Handling Pipeline
The `@handle_ice_errors` decorator in `app/exceptions.py` wraps endpoint functions:

| ZeroC Ice / Murmur Exception | HTTP Status Code | Description |
| :--- | :--- | :--- |
| `Murmur.InvalidSecretException` | `401 Unauthorized` | Invalid Ice administrative secret |
| `Murmur.ServerBootFailedException` | `400 Bad Request` | Murmur failed to boot virtual server |
| `Murmur.ServerCallbackException` | `400 Bad Request` | Callback failure inside Murmur |
| `Ice.ConnectionRefusedException` | `503 Service Unavailable` | Murmur daemon is unreachable or down |
| `Ice.ConnectTimeoutException` | `503 Service Unavailable` | Initial TCP connection timed out |
| `Ice.TimeoutException` | `504 Gateway Timeout` | Ice invocation timed out |
| `Ice.Exception` (generic) | `500 Internal Server Error` | Unexpected ZeroC Ice runtime failure |

---

## 5. Mock Ice Harness for Testing
Testing does not depend on a running Murmur server:
- `tests/mock_ice.py` implements complete in-memory mocks of `Murmur.MetaPrx` and `Murmur.ServerPrx`.
- `tests/conftest.py` configures the mock communicator in the test harness before tests run.
- Tests run seamlessly on any OS (Linux, macOS, Windows) without requiring native `python3-zeroc-ice` C extensions.

