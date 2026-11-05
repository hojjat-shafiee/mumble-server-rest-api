# Architecture Decision Records (ADR)

This directory documents key architectural decisions made in `mumble-server-rest-api`. Storing these records preserves context for future developers and prevents AI coding agents from inadvertently reversing fundamental design choices.

## Index of Decisions

| ADR | Title | Status | Date |
| :--- | :--- | :--- | :--- |
| [0001](0001-synchronous-ice-rpc-in-threadpool.md) | Synchronous ZeroC Ice RPC in Starlette Worker Threadpool | **Accepted** | 2026-11-05 |
| [0002](0002-mock-ice-stubs-for-cross-platform-testing.md) | Mock ZeroC Ice Stubs for Hermetic Cross-Platform Testing | **Accepted** | 2026-11-05 |
| [0003](0003-pydantic-v2-and-password-masking.md) | Pydantic v2 Schema Standardization & Password Masking | **Accepted** | 2026-11-05 |
| [0004](0004-multi-agent-instruction-architecture.md) | Multi-Agent Instruction Architecture & Repository Synchronization | **Accepted** | 2026-11-05 |

## Adding a New ADR

When making significant architectural changes:
1. Create a new markdown file named `XXXX-title-in-kebab-case.md`.
2. Follow standard ADR structure:
   - **Context**: Problem statement and forces driving the decision.
   - **Decision**: The chosen solution.
   - **Consequences**: Positive, neutral, and negative outcomes.
   - **Agent Compliance**: Rules AI agents must follow regarding this decision.
3. Update this index table and `llms.txt`.

