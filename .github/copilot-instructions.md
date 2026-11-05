# GitHub Copilot Instructions — mumble-server-rest-api

Repository-wide instructions for GitHub Copilot when generating code, suggesting edits, and reviewing pull requests for `mumble-server-rest-api`.

## Technical Context
- **Framework**: FastAPI (v0.111+) with Starlette and Uvicorn.
- **Python Version**: Python 3.11+
- **Data Validation**: Pydantic v2 (`from pydantic import BaseModel, Field, ConfigDict`).
- **Protocols & RPC**: ZeroC Ice 3.7 (`python3-zeroc-ice` / `Ice`), Murmur Slice RPC.
- **Test Suite**: Pytest with mock ZeroC Ice stubs in `tests/mock_ice.py`.

## Core Guidelines for Code Generation

### 1. Synchronous vs Asynchronous Functions (Crucial)
- **Always use synchronous `def` (not `async def`)** for any FastAPI route or dependency that calls ZeroC Ice RPC methods (e.g. `meta.getAllServers()`, `server.isRunning()`).
- ZeroC Ice uses blocking synchronous network sockets. FastAPI dispatches `def` endpoints to a background worker threadpool (`run_in_threadpool`), protecting the main async event loop.

### 2. Error Handling & Exception Decorator
- Wrap all route handlers with `@handle_ice_errors` from `app.exceptions`.
- Map domain errors accurately:
  - Missing server $\rightarrow$ `HTTPException(status_code=404, detail="Server ID X not found")`
  - Validation failures $\rightarrow$ `HTTPException(status_code=422, detail=...)`
  - Ice connection failures are handled by `@handle_ice_errors` and mapped to `503 Service Unavailable`.

### 3. Route Registration Order
- In `app/server_router.py`, register **static endpoints before dynamic parameterized paths**:
  - Valid: `/servers/version`, `/servers/deleteServers`, `/servers/userCount` defined BEFORE `/servers/{id}`.
  - Reason: FastAPI evaluates paths in order; defining `/{id}` first causes route masking or 422 integer parsing errors.

### 4. Dependency Injection
- Inject Ice Meta using `meta: Murmur.MetaPrx = Depends(get_ice_meta)`.
- Inject authentication for modifying routes (`POST`, `PATCH`, `DELETE`) using `_auth: bool = Depends(verify_api_key)`.

### 5. Pydantic v2 Models
- Use Pydantic v2 features: `model_config = ConfigDict(...)` instead of inner `class Config:`.
- Ensure responses use explicit `response_model` definitions from `app.models`.

### 6. Tests & Mocking
- Never add external network calls to tests in `tests/`.
- All tests must pass using the mock Ice stubs defined in `tests/mock_ice.py` and fixtures in `tests/conftest.py`.
- Run tests via `pytest` or `python -m pytest`.

### 7. Code Style & Formats
- Formatting: 4-space indentation, type hints on function signatures, clean docstrings.
- Imports order: standard library, third-party libraries (FastAPI, Pydantic), local application modules (`app`, `settings`).

