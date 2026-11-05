# FastAPI Implementation Instructions

These scoped instructions apply when editing or creating FastAPI endpoints, routers, dependencies, and middleware in `app/`.

## 1. Concurrency & Synchronous `def`
- **Rule**: Use standard synchronous `def` for any route handler that calls ZeroC Ice RPC methods (`meta.*`, `server.*`).
- **Explanation**: ZeroC Ice uses blocking socket operations. FastAPI automatically dispatches synchronous `def` endpoints to Starlette's worker threadpool (`run_in_threadpool`).
- **Forbidden**: Do NOT use `async def` when calling Ice RPC methods.

## 2. Route Registration Order
- Static routes must always be declared **before** dynamic parameterized routes in `app/server_router.py`:
  - `GET /servers/version`
  - `POST /servers/deleteServers`
  - `GET /servers/userCount`
  - All above routes must precede `GET /servers/{id}`.
- If static routes are placed after `/{id}`, FastAPI interprets strings like `"version"` as integer IDs, failing with `422 Unprocessable Entity`.

## 3. Exception Decorator
- Decorate every route calling Ice with `@handle_ice_errors` from `app.exceptions`.
- Return `HTTPException(status_code=404, detail="Server ID {id} not found")` when an entity is missing.

## 4. Response Models
- Always provide an explicit `response_model` argument in route decorators.
- Define response models in `app/models.py` using Pydantic v2.

