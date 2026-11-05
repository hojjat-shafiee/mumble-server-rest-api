# ADR 0003: Pydantic v2 Schema Standardization & Password Masking

- **Status**: Accepted
- **Date**: 2026-11-05
- **Deciders**: Engineering & AI Architecture

---

## Context
The legacy `Murmur-REST` application used untyped Flask dictionary responses and raw JSON serialization. This led to multiple vulnerabilities:
1. Murmur server passwords and Ice administrative secrets could be inadvertently returned in plain text in REST responses.
2. Lack of input validation allowed invalid configuration types to reach Murmur Slice stubs, triggering hard-to-debug Ice runtime exceptions.
3. Lack of schema definitions prevented automatic OpenAPI / Swagger documentation generation.

## Decision
We standardized all data models on **Pydantic v2**:
1. All request and response models inherit from `pydantic.BaseModel` and use `model_config = ConfigDict(extra="ignore")`.
2. Every route in `app/server_router.py` explicitly declares a `response_model`.
3. Server configuration serialization respects `settings.MASK_PASSWORDS`. When `True` (default), the `serverpassword` property and sensitive configuration keys are masked as `"***"` before being sent to callers.
4. An `obj_to_dict` utility in `app/utils.py` handles recursive conversion of Ice Slice types, Python dictionaries, and `__slots__` structures safely without `AttributeError`.

## Consequences
### Positive
- Fully documented OpenAPI 3.0 schema at `/docs` and `/redoc`.
- Strict validation of inputs before calling Ice RPC methods.
- Guaranteed protection of server passwords in public and private responses.

### Negative / Trade-offs
- Slight overhead of Pydantic parsing, which is negligible compared to network RPC latency.

## Agent Compliance Rules
1. Use Pydantic v2 conventions (`model_config = ConfigDict(...)`), not deprecated v1 `class Config:`.
2. Ensure password masking logic in endpoints or helper functions is preserved when returning server detail configurations.
3. Do not return raw Slice objects directly from endpoints; use Pydantic response models.

