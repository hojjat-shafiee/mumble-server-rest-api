# ADR 0004: Multi-Agent Instruction Architecture & Repository Synchronization

- **Status**: Accepted
- **Date**: 2026-11-05
- **Deciders**: Engineering & AI Architecture

---

## Context
Modern software engineering utilizes diverse AI coding assistants across developer environments:
- Claude Code CLI (`CLAUDE.md`)
- GitHub Copilot & Copilot Workspace (`.github/copilot-instructions.md`, `.github/instructions/`)
- Cursor IDE (`.cursorrules`, `.cursor/rules/*.mdc`)
- Windsurf Cascade (`.windsurfrules`, `.windsurf/rules/rules.md`)
- Cline & Roo Code (`.clinerules`, `.roomodes`)
- Aider CLI (`.aider.conf.yml`)
- Machine context standards (`llms.txt`, `llms-full.txt`, `docs/repository-map.md`)

Without a deliberate synchronization strategy, instructions diverge across agent files, causing inconsistent code generation, hallucinated patterns, or contradictory instructions.

## Decision
We establish a layered multi-agent instruction architecture:
1. **Single Source of Truth**: `AGENTS.md` at root serves as the primary cross-tool specification and ground truth for all architectural guardrails.
2. **Tool-Specific Adapters**: Tool-specific files (`CLAUDE.md`, `.cursorrules`, `.windsurfrules`, `.clinerules`, `.roomodes`) concisely map `AGENTS.md` directives to the specific execution context and syntax expected by each tool.
3. **Machine Ingestion Standards**: `llms.txt` and `llms-full.txt` adhere strictly to the `llmstxt.org` specification to enable high-efficiency RAG and agent context intake.
4. **Token-Optimized Repository Map**: `docs/repository-map.md` provides an index of symbols and call flows to eliminate token waste from full directory traversals.
5. **Deterministic Verification Script**: `scripts/verify.py` and `make check` give all agents a single idempotent command to test and lint the repository before concluding turns.

## Consequences
### Positive
- Consistent behavior regardless of which AI coding tool or developer environment is used.
- Drastic reduction in token consumption and inference latency.
- Elimination of prompt drift and contradictory rules.

### Negative / Trade-offs
- Modifying architectural rules requires updating both `AGENTS.md` and the relevant adapter files.

## Agent Compliance Rules
1. When modifying instructions or adding new architectural conventions, update `AGENTS.md` first, then propagate changes to `CLAUDE.md`, `.clinerules`, `.cursorrules`, and `.windsurfrules`.
2. Do not introduce bloated or conflicting rules into tool-specific config files.

