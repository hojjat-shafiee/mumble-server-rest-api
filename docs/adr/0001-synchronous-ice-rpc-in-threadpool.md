# ADR 0001: Synchronous ZeroC Ice RPC in Starlette Worker Threadpool

- **Status**: Accepted
- **Date**: 2026-11-05
- **Deciders**: Engineering & AI Architecture

---

## Context
Murmur (the Mumble VoIP server daemon) provides an RPC interface via ZeroC Ice 3.7. The official Python extension (`Ice` / `python3-zeroc-ice`) is a compiled C++ wrapper that executes blocking socket network calls.

FastAPI is built on Starlette and `asyncio`. When developers or AI coding agents write route functions in FastAPI, the common default assumption is to declare them with `async def`. However:
1. Calling a synchronous blocking function (such as ZeroC Ice RPC methods) inside an `async def` route runs directly on the main event loop thread.
2. This blocks the entire asyncio event loop during network I/O, preventing other HTTP connections from being handled and creating severe latency or complete application hang.

## Decision
We mandate that **all FastAPI route handlers that interact with ZeroC Ice RPC proxies must be declared using standard synchronous `def` functions**, not `async def`.

FastAPI natively inspects whether an endpoint is defined with `def` or `async def`. For synchronous `def` endpoints, FastAPI automatically offloads execution to Starlette's threadpool (`run_in_threadpool`), leaving the main event loop free to accept incoming HTTP requests concurrently.

Pure in-memory endpoints (such as `GET /` and `GET /healthz` when not probing Ice) may remain `async def`.

## Consequences
### Positive
- ZeroC Ice blocking socket calls are executed in isolated worker threads.
- Event loop starvation is completely avoided.
- High concurrent HTTP throughput is preserved.

### Negative / Trade-offs
- AI agents with naive prompt priors tend to default to `async def` in FastAPI. Explicit instruction files, linters, and verification checks must actively enforce this convention.

## Agent Compliance Rules
1. Never convert an endpoint calling `meta.*` or `server.*` to `async def`.
2. Any newly implemented route interacting with ZeroC Ice must use synchronous `def`.
3. Wrap all such route handlers with `@handle_ice_errors`.

