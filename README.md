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

## Features (Planned)

### Phase 1: CLI Application (Current)
- [x] Project structure and documentation
- [ ] Core poker engine (hand evaluation, equity calculations)
- [ ] Hand history parser
- [ ] AI coaching integration
- [ ] Range management system
- [ ] Quiz engine
- [ ] Session and bankroll tracking

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

### Current (Phase 1)
- **Language**: Python 3.11+
- **CLI Framework**: Typer
- **UI**: Rich (terminal interface)
- **Database**: SQLite
- **AI/LLM**: Anthropic Claude API
- **Testing**: pytest
- **Code Quality**: black, ruff, pyrefly

### Future (Phase 2 & 3)
- **Backend**: FastAPI, PostgreSQL
- **Frontend**: Next.js, TypeScript, React, TailwindCSS
- **Deployment**: Vercel (frontend), Railway/Render (backend)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/poker-agent.git
cd poker-agent

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (when available)
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Usage

*Coming soon - CLI interface is under development*

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run code quality checks
black .
ruff check .
pyrefly .
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
├── src/                    # Source code
│   ├── core/              # Poker engine (hand eval, equity, ranges)
│   ├── analysis/          # Hand analysis & coaching
│   ├── study/             # Quiz engine, progress tracking
│   ├── ranges/            # Range management
│   ├── bankroll/          # Session & bankroll tracking
│   ├── agent/             # AI coaching agent
│   └── cli/               # CLI interface
├── tests/                 # Test suite
├── docs/                  # Documentation
├── .github/               # GitHub templates and workflows
├── SYSTEM_DESIGN.md       # Detailed system design
├── CONTRIBUTING.md        # Contribution guidelines
└── README.md             # This file
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
- ⏳ Core poker engine implementation
- ⏳ CLI application (hand analysis, ranges, quizzes)
- ⏳ AI coaching integration

### Q2 2025
- FastAPI backend development
- Database design and migration
- API endpoint implementation
- Authentication system

### Q3 2025
- Next.js frontend development
- Mobile-responsive UI
- Hand replayer and visualization
- Dashboard and analytics

### Q4 2025
- Beta testing and refinement
- Performance optimization
- Production deployment
- Public launch

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

**Current Phase**: Phase 1 - CLI Application Development
**Last Updated**: December 25, 2025
**Version**: 0.1.0-alpha (pre-release)

---
