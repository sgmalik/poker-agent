# Library Reference Documentation

This directory contains reference documentation for all external libraries used in the Poker Coach Agent application.

## Library Overview

| Library | Version | Purpose | Module Usage |
|---------|---------|---------|--------------|
| Textual | 0.40+ | Terminal UI framework | `src/tui/` |
| SQLAlchemy | 2.0+ | Database ORM | `src/database/` |
| treys | 0.1.8 | Poker hand evaluation | `src/core/` |
| LangChain | 0.1+ | AI agent framework | `src/agent/`, `src/tools/` |
| langchain-anthropic | 0.1+ | Anthropic integration | `src/agent/` |

## Documentation Files

- [Textual](./textual.md) - Terminal UI framework
- [SQLAlchemy](./sqlalchemy.md) - Database ORM and query language
- [treys](./treys.md) - Poker hand evaluation library
- [LangChain](./langchain.md) - AI agent and tool framework

## Installation

All dependencies are managed via `pyproject.toml` and installed with:

```bash
uv sync
```

Or with pip:

```bash
pip install -e .
```
