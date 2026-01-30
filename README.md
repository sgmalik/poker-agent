# Poker Coach Agent

> **⚠️ Work in Progress**: This project is currently in active development. Features and APIs are subject to change.

An AI-powered poker coaching and study platform designed to help players improve their game through personalized hand analysis, strategic guidance, and interactive learning tools.

## Overview

Poker Coach Agent combines advanced poker theory with AI-powered coaching to provide players with:

- **Hand Analysis**: Upload and analyze your poker hands with detailed strategic breakdowns
- **Range Exploration**: Build, visualize, and study optimal ranges for different scenarios
- **Interactive Quizzes**: Test your knowledge with scenario-based questions and immediate feedback
- **Session Tracking**: Monitor your results, variance, and bankroll management
- **AI Coaching**: Get personalized strategic advice from an AI coach trained on GTO principles

## Features

### Phase 1: TUI Application (Complete)
- [x] Project structure and documentation
- [x] Core poker engine (hand evaluation, equity calculations, outs, pot odds)
- [x] Mode 1: Hand Evaluator & Spot Analyzer
- [x] Mode 2: Range Tools (GTO charts, range parser, 13x13 matrix visualization)
- [x] Mode 3: Quiz System (80 questions, 8 topics, database persistence)
- [x] Mode 4: Session Tracker (bankroll graphs, stats dashboard)
- [x] Mode 5: Hand History Manager (tagging, search, pattern analysis)
- [x] Mode 6: AI Agent Coach (LangChain integration, tool calling)

### Phase 2: Backend API
- [ ] FastAPI REST API
- [ ] Multi-user support
- [ ] Authentication and authorization
- [ ] Database (PostgreSQL)
- [ ] API documentation

### Phase 3: Web Application
- [ ] Next.js frontend
- [ ] Mobile-responsive design
- [ ] Interactive hand replayer
- [ ] Graphical range visualization
- [ ] Dashboard and analytics
- [ ] Progressive Web App (PWA)

## Technology Stack

- **Language**: Python 3.12+
- **Package Manager**: uv
- **TUI Framework**: Textual (full-screen terminal UI)
- **Database**: SQLite with SQLAlchemy ORM
- **Poker Engine**: treys (hand evaluation)
- **AI/LLM**: LangChain + Anthropic Claude API
- **Testing**: pytest (415+ tests)
- **Code Quality**: black, ruff, pyrefly

## Getting Started

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/sgmalik/poker-agent.git
cd poker-agent

# Install dependencies with uv
uv sync

# Set up environment variables (required for AI Agent Coach)
cp .env.example .env
# Edit .env with your Anthropic API key
```

### Usage

```bash
# Run the TUI application
uv run python -m src.tui.app

# Or after installation
poker-coach
```

### Application Modes

1. **Hand Evaluator & Spot Analyzer** - Analyze hand strength, equity, pot odds, EV
2. **Range Tools** - Explore GTO preflop ranges with visual 13x13 matrix
3. **Quiz System** - Test your poker knowledge with 80 scenario-based questions
4. **Session Tracker** - Log sessions and track bankroll with graphs
5. **Hand History Manager** - Store, tag, and analyze your hands
6. **AI Agent Coach** - Chat with an AI coach that has access to all tools

## Development

### Setup Development Environment

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run code quality checks
uv run black .
uv run ruff check .
uv run pyrefly check src/
```

### Git Hooks

This project uses pre-commit hooks to ensure code quality. The hook automatically runs:
- Code formatting (black)
- Linting (ruff)
- Type checking (pyrefly)
- Tests (pytest)

All checks must pass before commits are allowed.

### Project Structure

```
poker-agent/
├── src/
│   ├── core/              # Poker logic (hand_evaluator, spot_analyzer, range_parser, etc.)
│   ├── quiz/              # Quiz engine
│   ├── database/          # SQLAlchemy models and service layer
│   ├── tools/             # LangChain tool wrappers for AI agent
│   ├── agent/             # LangChain agent setup (coach.py, prompts.py)
│   └── tui/               # Textual TUI application
│       ├── app.py         # Main app with mode selection
│       └── screens/       # Mode-specific screens (mode1-6)
├── tests/                 # Test suite (415+ tests)
├── data/                  # GTO ranges, quiz questions
├── docs/                  # Library reference documentation
├── .claude/               # Claude Code configuration
├── BUILD_CHARTER.md       # Feature specifications
├── CONTRIBUTING.md        # Contribution guidelines
└── README.md              # This file
```

## Contributing

Contributions are welcome! This is an active learning project and collaboration is encouraged.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on:
- Code of conduct
- Development workflow
- Code quality standards
- Testing requirements
- Poker logic validation

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run quality checks (`black . && ruff check . && pyrefly . && pytest`)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Documentation

- [System Design](SYSTEM_DESIGN.md) - Comprehensive architecture and technical design
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the project
- API Documentation - *Coming soon*
- User Guide - *Coming soon*

## Roadmap

### Q1 2025
- ✅ Project setup and documentation
- ✅ Core poker engine (hand evaluation, equity, outs, pot odds)
- ✅ TUI application with all 6 modes
- ✅ AI coaching integration with LangChain

### Future Enhancements
- Range-based equity calculator
- Mixed frequency hands with hover tooltips
- Spaced repetition for quiz system
- Hand history import/export (PokerStars, GGPoker formats)

## License

*License to be determined*

## Acknowledgments

- Poker strategy resources: Run It Once, Upswing Poker, Two Plus Two
- Poker libraries: treys, poker
- AI/LLM: Anthropic Claude
- Inspiration: GTO Wizard, PokerSnowie, and the poker community

## Contact

- **Author**: [Surya Malik]
- **Email**: [malik.g.surya@gmail.com]
- **GitHub**: [@sgmalik](https://github.com/sgmalik)

## Status

**Current Phase**: Phase 1 Complete - All 6 Modes Implemented
**Last Updated**: January 29, 2026
**Version**: 0.1.0-alpha

---
