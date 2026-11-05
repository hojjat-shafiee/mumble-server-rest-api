# Agent Coding Workflow — mumble-server-rest-api

Step-by-step guidance for AI agents implementing features, fixing bugs, or writing tests in this codebase.

---

## 1. Feature Implementation Flow

When adding or modifying an endpoint:

1. **Check Route Registration Order**:
   - In `app/server_router.py`, ensure static paths are defined **before** `/{id}` parameterized paths.
2. **Define Pydantic Schemas**:
   - In `app/models.py`, define request models and response models using Pydantic v2.
   - Use `model_config = ConfigDict(extra="ignore")`.
3. **Implement Synchronous Route**:
   - Use `def route_name(...)` (never `async def` when calling Ice).
   - Add `@handle_ice_errors` decorator.
   - Add `_auth: bool = Depends(verify_api_key)` if the route modifies state (`POST`, `PATCH`, `DELETE`).
   - Inject `meta: Murmur.MetaPrx = Depends(get_ice_meta)`.
4. **Update Mock Stubs if Needed**:
   - If calling a new method on Murmur Meta or Server, ensure the method is supported in `tests/mock_ice.py`.
5. **Add Tests**:
   - Add unit/API tests in `tests/test_api.py`.
   - Test success status codes, not-found (404), validation errors (422), and authentication (401).
6. **Run Verification Loop**:
   ```bash
   pytest
   ```

---

## 2. Common Gotchas & Fixes

| Issue | Cause | Fix |
| :--- | :--- | :--- |
| `Event loop blocked` | Using `async def` with Ice calls | Change endpoint to synchronous `def` |
| `422 Unprocessable Entity` on static path | Static route defined after `/{id}` | Move static route above parameterized route in `app/server_router.py` |
| `AttributeError` during serialization | Accessing missing Slice attributes | Use `obj_to_dict` in `app/utils.py` |
| Password exposed in API response | Missing masking check | Check `settings.MASK_PASSWORDS` and replace password with `"***"` |
| `ModuleNotFoundError` running pytest | Python path not resolving root | Verify `pyproject.toml` contains `pythonpath = ["."]` |

---

## 3. Pre-Commit Checklist for Agents

Before completing a task, verify:
- [ ] `pytest` passes with 0 failures and 0 errors.
- [ ] No `async def` route handlers call ZeroC Ice proxies directly.
- [ ] No manual edits were made to `Murmur_ice.py`.
- [ ] Legacy compatibility endpoints are preserved.
- [ ] New routes have `response_model` and OpenAPI docstrings.

