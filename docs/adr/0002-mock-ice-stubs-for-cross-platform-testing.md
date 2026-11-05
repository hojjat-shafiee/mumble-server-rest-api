# ADR 0002: Mock ZeroC Ice Stubs for Hermetic Cross-Platform Testing

- **Status**: Accepted
- **Date**: 2026-11-05
- **Deciders**: Engineering & AI Architecture

---

## Context
ZeroC Ice 3.7 Python bindings (`zeroc-ice` / `python3-zeroc-ice`) require pre-compiled C++ extension binaries matching specific Python versions and system architectures. While Debian packages exist (`python3-zeroc-ice`), installing native ZeroC Ice on modern developer workstations (Windows 11, macOS ARM64) or lightweight CI runners without Debian apt is extremely difficult, error-prone, or impossible for Python 3.12+.

Furthermore, running integration tests against a live Murmur daemon requires root socket bindings, configuration state resets, and introduces network instability into CI.

## Decision
We established a high-fidelity **Mock Ice Subsystem** in `tests/mock_ice.py`:
1. `MockCommunicator`: Simulates Ice communicator initialization, properties, and shutdown.
2. `MockMetaPrx`: Simulates the Murmur `MetaPrx` proxy, maintaining in-memory virtual servers, version tuples, and boot callbacks.
3. `MockServerPrx`: Simulates virtual `ServerPrx` instances with state (`running`), user counts, configuration maps, and log buffers.
4. `mock_ice_meta` Pytest Fixture: Injects the mock proxy into `app.ice_manager.ice_manager` via `set_meta()`.

## Consequences
### Positive
- Tests can run on any platform (Windows, macOS, Linux, Devcontainers) without native ZeroC Ice compiled libraries.
- The test suite runs in under 1 second (100% hermetic, zero network sockets).
- Edge cases (Ice connection drops, timeouts, boot failures, secret errors) are easily simulated deterministically.
- AI agents can run `pytest` locally in sandbox environments without needing access to Docker or external Murmur servers.

### Negative / Trade-offs
- Mock stubs must be kept synchronized if new Murmur Slice RPC methods are used.

## Agent Compliance Rules
1. Never write tests that attempt to connect to a live Murmur daemon over port 6502.
2. Use the `mock_ice_meta` fixture and `tests/mock_ice.py` for all API tests.
3. If new Murmur RPC methods are called in `app/`, add corresponding mock method signatures to `MockMetaPrx` or `MockServerPrx`.

