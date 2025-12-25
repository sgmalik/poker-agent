# Poker Coach Agent - Project Context

## Project Overview
This is a comprehensive poker coaching and study tool featuring AI-powered hand analysis, range exploration, quiz-based learning, and bankroll management. The goal is to create a professional tool for poker players to improve their game through data-driven insights and personalized coaching.

## Architecture Summary

### Current Phase: Phase 1 (CLI Development)
Building the core poker engine and CLI interface for rapid development and testing.

### Future Phases:
- **Phase 2**: FastAPI backend with REST API
- **Phase 3**: Next.js/TypeScript frontend for web/mobile/tablet
- **Phase 4**: Production deployment and polish

## Tech Stack

### Phase 1 (Current)
- **Language**: Python 3.11+
- **CLI Framework**: Typer
- **CLI UI**: Rich (for beautiful terminal output)
- **Database**: SQLite (local development)
- **LLM Integration**: Anthropic Claude API (primary)
- **Testing**: pytest, pytest-cov
- **Code Quality**: black, ruff, pyrefly

### Phase 2 & 3 (Future)
- **Backend**: FastAPI + PostgreSQL
- **Frontend**: Next.js 14+ (TypeScript, React, TailwindCSS, shadcn/ui)
- **Deployment**: Vercel (frontend), Railway/Render (backend)

## Project Structure

```
poker-agent/
├── src/
│   ├── core/              # Poker engine (hand eval, equity, ranges)
│   ├── analysis/          # Hand analysis & coaching
│   ├── study/             # Quiz engine, progress tracking
│   ├── ranges/            # Range management & visualization
│   ├── bankroll/          # Session & bankroll tracking
│   ├── agent/             # AI coaching agent
│   └── cli/               # CLI interface
├── tests/                 # Test suite
├── data/                  # User data (hands, sessions, progress)
├── config/                # Configuration files
└── docs/                  # Documentation
```

## Key Design Principles

1. **Modular Components**: Each module (core, analysis, study, etc.) should be independent and testable
2. **Type Safety**: Use Python type hints everywhere, enforce with mypy
3. **Test Coverage**: Aim for 100% coverage on poker logic (hand evaluation, equity calculations)
4. **CLI First**: Build and validate features in CLI before building web UI
5. **Performance**: Optimize equity calculations and hand analysis (target <1s per hand)
6. **User-Centric**: Design for poker players - clear feedback, actionable insights

## Important Conventions

### Code Style
- **Formatting**: black (line length: 100)
- **Linting**: ruff with strict settings
- **Type Checking**: mypy in strict mode
- **Docstrings**: Google-style docstrings for all public functions/classes
- **Naming**:
  - snake_case for functions/variables
  - PascalCase for classes
  - UPPER_CASE for constants

### Testing
- **Unit Tests**: All core poker logic must have unit tests
- **Integration Tests**: Test workflows (parse hand → analyze → provide coaching)
- **Fixtures**: Use pytest fixtures for common test data (hands, ranges, etc.)
- **Mocking**: Mock LLM API calls in tests to avoid costs

### Database
- **ORM**: Use SQLAlchemy for all database operations
- **Migrations**: Alembic for schema changes
- **Transactions**: Use transactions for multi-step operations
- **Indexes**: Index frequently queried fields (user_id, timestamp, tags)

### Git Workflow
- **Branches**: Feature branches from main (e.g., `feature/hand-evaluator`)
- **Commits**: Conventional commits (e.g., `feat: add equity calculator`, `fix: hand evaluation bug`)
- **PRs**: All changes via pull requests (even solo dev - good practice)
- **CI**: Run tests and linting on every commit

## Poker-Specific Context

### Game Focus
- **Primary**: No-Limit Texas Hold'em (cash games)
- **Future**: Tournaments, PLO, other variants

### Strategic Framework
- **GTO Foundation**: Base recommendations on GTO principles
- **Exploitative Adjustments**: Allow for player-specific adjustments
- **Stake Awareness**: Tailor advice to stake level (micro, small, mid, high)

### Key Poker Concepts to Implement
- **Equity calculations**: Monte Carlo simulations for hand vs hand, hand vs range, range vs range
- **Range notation**: Support standard notation (e.g., "AK, QQ+, 98s+, A5s-A2s")
- **Position awareness**: UTG, MP, CO, BTN, SB, BB
- **Bet sizing**: Analyze sizing in context of pot odds, stack-to-pot ratio
- **Hand reading**: Help users narrow opponent ranges based on actions

## Common Gotchas

### Poker Logic
- **Suits**: Ensure consistent suit notation (s=spades, h=hearts, d=diamonds, c=clubs)
- **Hand strength**: 7-card evaluation for Hold'em (2 hole cards + 5 board cards)
- **Equity**: Always show equity as percentage (e.g., 65.3%, not 0.653)
- **Dead cards**: Account for known cards when calculating equity

### LLM Integration
- **Cost Management**: Count tokens before API calls, cache responses where possible
- **Prompt Engineering**: Include poker-specific context in system prompts
- **Error Handling**: Gracefully handle API failures, rate limits, timeouts
- **Streaming**: Use streaming for long coaching responses (better UX)

### Performance
- **Equity Calculations**: Can be slow for range vs range - show progress bars
- **Hand Parsing**: Validate format early to avoid processing invalid data
- **Database Queries**: Use pagination for large datasets (hand histories)

## Development Workflow

### Starting a New Feature
1. Check SYSTEM_DESIGN.md for requirements
2. Create feature branch
3. Write tests first (TDD approach for core logic)
4. Implement feature
5. Run full test suite
6. Update documentation if needed
7. Create PR (even if solo, for practice)

### Before Committing
1. Run `black .` for formatting
2. Run `ruff check .` for linting
3. Run `pyrefly .` for type checking
4. Run `pytest` for all tests
5. Check test coverage with `pytest --cov`

### When Adding Dependencies
1. Add to `requirements.txt` (or `pyproject.toml` if using)
2. Document why it's needed
3. Check for license compatibility
4. Pin versions for reproducibility

## AI Coaching Agent Specifics

### LLM Provider
- **Primary**: Anthropic Claude (Sonnet for coaching, Haiku for simple tasks)
- **Fallback**: OpenAI GPT-4 (if Claude unavailable)

### Prompt Strategy
- **System Prompt**: Establish poker expertise, teaching style, format preferences
- **Context**: Include hand history, user stats, identified leaks
- **Few-Shot Examples**: Provide example hand analyses in prompts
- **Token Limits**: Keep responses under 1000 tokens for cost control

### Coaching Modes
- **Hand Review**: Detailed analysis of specific hands
- **Concept Explanation**: Answer strategic questions
- **Quiz Feedback**: Explain quiz answers with strategic reasoning
- **Study Plan**: Generate personalized study recommendations

## Data Privacy & Security

### User Data
- **Local Storage**: Phase 1 stores all data locally (SQLite)
- **No Sharing**: Never share user data without explicit consent
- **API Keys**: Store in `.env` file (never commit), use environment variables

### Security Checklist (for Phase 2+)
- [ ] Hash passwords with bcrypt
- [ ] Use JWT for authentication
- [ ] Validate all user inputs
- [ ] Rate limit API endpoints
- [ ] Enable CORS properly
- [ ] Use HTTPS only in production
- [ ] Sanitize hand history inputs (prevent injection)

## Resources & References

### Quick Links
- [System Design Document](../SYSTEM_DESIGN.md)
- [Anthropic Claude API Docs](https://docs.anthropic.com/)
- [treys library](https://github.com/ihendley/treys) - Hand evaluation
- [Rich library](https://rich.readthedocs.io/) - Terminal UI
- [Typer docs](https://typer.tiangolo.com/) - CLI framework

### Poker Strategy References
- Use GTO Wizard for range validation
- Two Plus Two forums for strategic discussions
- Upswing Poker for modern strategy concepts

## Current Development Focus

### Immediate Priorities (Phase 1)
1. **Core Poker Engine**: Hand evaluation, equity calculations, range operations
2. **Hand History Parser**: Support PokerStars and manual entry formats
3. **Basic AI Coach**: Simple hand review with Claude integration
4. **CLI Interface**: Clean, intuitive command structure

### Next Steps
- Range visualization (ASCII grid)
- Quiz engine with question bank
- Session tracking and bankroll management
- Progress tracking and spaced repetition

## Known Limitations & TODOs

### Current Limitations
- Only supports Texas Hold'em (no PLO, Omaha, etc.)
- CLI only (no web UI yet)
- Single user (no multi-user support)
- English only (no i18n)

### Technical Debt to Address
- None yet (greenfield project)

### Future Considerations
- Tournament-specific features (ICM calculations)
- Opponent modeling and tracking
- Integration with poker tracking software
- Mobile apps (React Native)

## Questions & Decisions Log

### Decision: CLI First Approach
- **Why**: Faster iteration, validate core features before building web UI
- **Trade-off**: Users need terminal access (less accessible)
- **Future**: Will build web UI in Phase 3

### Decision: Claude API as Primary LLM
- **Why**: Superior reasoning for poker strategy, better context handling
- **Trade-off**: Slightly higher cost than GPT-4
- **Future**: May add GPT-4 as fallback option

### Decision: Next.js for Frontend
- **Why**: Best-in-class React framework, mobile-optimized, TypeScript support
- **Trade-off**: Learning curve for frontend development
- **Future**: Consider React Native for native mobile apps

## Tips for Claude Code

### When Making Changes
- Always read files before editing (use Read tool)
- Run tests after changes to poker logic
- Update this context file if major architectural decisions change
- Keep SYSTEM_DESIGN.md in sync with implementation

### File Organization
- Keep modules focused and single-purpose
- Prefer many small files over few large files
- Group related functionality (e.g., all equity calculations in one module)

### Testing Strategy
- Test poker calculations against known results (use online equity calculators)
- Mock external APIs (LLM, database) in unit tests
- Use integration tests for end-to-end workflows

---

**Last Updated**: 2025-12-25
**Phase**: 1 (CLI Development)
**Status**: Active Development
