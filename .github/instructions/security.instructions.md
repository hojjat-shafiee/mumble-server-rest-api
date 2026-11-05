# Security & Credential Handling Instructions

These instructions govern authentication, authorization, and secret handling across the API.

## 1. Authentication on Modifying Endpoints
- Mutating HTTP methods (`POST`, `PATCH`, `DELETE`) must require authentication:
  ```python
  _auth: bool = Depends(verify_api_key)
  ```
- `verify_api_key` supports:
  - Header: `X-API-Key: <token>`
  - Header: `Authorization: Bearer <token>`
- If `settings.API_KEY` is empty, authentication is bypassed for local developer convenience.

## 2. Password Masking
- When returning server configuration dictionaries or detail objects:
  - Check `settings.MASK_PASSWORDS`.
  - If `True`, replace the server password (`serverpassword` property or configuration field) with `"***"`.
- Never expose cleartext passwords in API responses when masking is enabled.

## 3. Secret Protection
- Never log raw passwords, Murmur `ICE_SECRET`, or `API_KEY` values to stdout, stderr, or application loggers.
- Keep `.env` files in `.gitignore`.

