# Testing & Verification Instructions

These instructions guide the authoring, execution, and verification of tests in `tests/`.

## 1. Test Isolation & Mock Stubs
- Never make live network socket connections in tests.
- All tests must run hermetically against the mock ZeroC Ice implementation in `tests/mock_ice.py`.
- Rely on the `mock_ice_meta` fixture in `tests/conftest.py`, which injects `MockMetaPrx` into `app.ice_manager.ice_manager`.

## 2. Test Execution
- Run tests using `pytest` or `python -m pytest`.
- Configuration is loaded from `pyproject.toml` (which configures `pythonpath = ["."]`).
- Aim for 100% test pass rate with 0 errors and 0 failures.

## 3. Test Coverage Requirements
When adding or altering endpoints, test:
1. **Happy path**: Verify 200/201 response status, schema keys, and payload.
2. **Not found (404)**: Verify non-existent IDs return 404 with standard error detail.
3. **Validation error (422)**: Verify malformed input is caught by Pydantic.
4. **Authentication (401)**: Verify unauthorized mutating requests are rejected when `API_KEY` is set.
5. **Exception mapping**: Verify `@handle_ice_errors` correctly translates Ice exceptions to HTTP status codes.

